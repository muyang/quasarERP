
"""
生产工单物料齐套性检查模块

在 Work Order 提交前检查所有 required_items 的库存可用量。
若有短缺，阻止提交并生成缺料清单。
"""

import frappe
from frappe import _
from frappe.utils import flt


def check_material_availability(doc, method):
    """
    Work Order before_submit: 检查 BOM 物料库存是否足够
    """
    if not doc.required_items:
        return  # 没有 BOM 物料，跳过检查

    shortage_items = []

    for item in doc.required_items:
        item_code = item.item_code
        warehouse = item.source_warehouse or doc.wip_warehouse
        required_qty = flt(item.required_qty) - flt(item.transferred_qty)

        if required_qty <= 0:
            continue

        # 获取实际可用库存
        available_qty = get_available_stock(item_code, warehouse)

        if available_qty < required_qty:
            shortage_qty = required_qty - available_qty

            # 获取建议供应商（取 Item Default 中的供应商）
            suggested_supplier = get_default_supplier(item_code)

            shortage_items.append({
                "item_code": item_code,
                "item_name": item.item_name or frappe.db.get_value("Item", item_code, "item_name"),
                "warehouse": warehouse,
                "required_qty": required_qty,
                "available_qty": available_qty,
                "shortage_qty": shortage_qty,
                "suggested_supplier": suggested_supplier,
            })

    if shortage_items:
        # 创建缺料清单
        shortage_list = frappe.get_doc({
            "doctype": "Material Shortage List",
            "work_order": doc.name,
            "production_item": doc.production_item,
            "status": "待处理",
            "items": shortage_items,
        })
        shortage_list.insert(ignore_permissions=True)

        # 阻止提交并显示缺料信息
        item_details = "<br>".join(
            f"• {item['item_code']}: 需要 {item['required_qty']} / 可用 {item['available_qty']} / 缺 {item['shortage_qty']} (仓库: {item['warehouse']})"
            for item in shortage_items
        )

        frappe.throw(
            _(
                "物料不齐套，无法提交生产工单！<br><br>"
                "<b>缺料清单已生成：{0}</b><br><br>"
                "{1}<br><br>"
                "请处理缺料后再提交，或在缺料清单中一键生成采购申请。"
            ).format(shortage_list.name, item_details),
            title=_("物料不齐套"),
        )


def get_available_stock(item_code, warehouse=None):
    """
    获取物料的实际可用库存
    使用 erpnext 内置函数，排除已预留库存
    """
    from erpnext.stock.utils import get_stock_balance

    if not warehouse:
        # 如果没有指定仓库，获取所有仓库总库存
        warehouses = frappe.get_all("Warehouse", filters={"is_group": 0}, pluck="name")
    else:
        warehouses = [warehouse]

    total_actual = 0.0
    total_reserved = 0.0

    for wh in warehouses:
        actual = get_stock_balance(item_code, wh)
        if actual:
            total_actual += flt(actual)

        # 获取预留量
        reserved = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": wh}, "reserved_qty") or 0
        total_reserved += flt(reserved)

    return total_actual - total_reserved


def get_default_supplier(item_code):
    """获取物料的首选供应商"""
    suppliers = frappe.get_all(
        "Item Supplier",
        filters={"parent": item_code},
        fields=["supplier"],
        order_by="idx",
        limit=1,
    )
    if suppliers:
        return suppliers[0].supplier
    return None


@frappe.whitelist()
def generate_purchase_request(docname):
    """
    从缺料清单一键生成采购申请 (Material Request)
    在客户端按钮中调用
    """
    shortage_list = frappe.get_doc("Material Shortage List", docname)

    if shortage_list.status != "待处理":
        frappe.throw(_("该缺料清单已处理，无法重复生成采购申请。"))

    mr_items = []
    for item in shortage_list.items:
        # 跳过已有采购申请的
        if item.purchase_request:
            continue

        mr_items.append({
            "item_code": item.item_code,
            "item_name": item.item_name,
            "warehouse": item.warehouse,
            "qty": item.shortage_qty,
            "schedule_date": frappe.utils.add_days(frappe.utils.today(), 7),
            "uom": frappe.db.get_value("Item", item.item_code, "stock_uom"),
            "work_order": shortage_list.work_order,
        })

    if not mr_items:
        frappe.throw(_("所有物料已生成采购申请，无需重复操作。"))

    mr = frappe.get_doc({
        "doctype": "Material Request",
        "material_request_type": "Purchase",
        "schedule_date": frappe.utils.add_days(frappe.utils.today(), 7),
        "items": mr_items,
        "set_from_warehouse": None,
        "remarks": _("由缺料清单 {0} (工单 {1}) 自动生成").format(
            shortage_list.name, shortage_list.work_order
        ),
    })
    mr.insert(ignore_permissions=True)

    # 更新缺料清单中各项的采购申请引用
    for item in shortage_list.items:
        if not item.purchase_request:
            item.purchase_request = mr.name

    shortage_list.status = "采购申请已生成"
    shortage_list.save(ignore_permissions=True)

    frappe.msgprint(
        _("已生成采购申请 <b>{0}</b>，包含 {1} 项缺料物料。").format(
            mr.name, len(mr_items)
        ),
        alert=True,
    )

    return mr.name
