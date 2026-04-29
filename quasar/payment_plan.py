"""
采购订单 hooks：自动生成 / 取消付款计划

在 Purchase Order 提交时读取 Payment Terms，按比例生成 PaymentPlan 记录；
在 Purchase Order 取消时同步取消关联的付款计划。
"""

import frappe
from frappe import _
from frappe.utils import add_days, getdate


def generate_payment_plans(doc, method):
    """
    Purchase Order on_submit: 根据 payment_schedule 生成付款计划
    """
    if not doc.payment_schedule or len(doc.payment_schedule) == 0:
        return

    created_count = 0
    for schedule in doc.payment_schedule:
        if schedule.payment_amount <= 0:
            continue

        payment_plan = frappe.get_doc({
            "doctype": "Payment Plan",
            "supplier": doc.supplier,
            "purchase_order": doc.name,
            "planned_payment_date": getdate(schedule.due_date) if schedule.due_date else doc.transaction_date,
            "amount": schedule.payment_amount,
            "status": "Pending",
            "remarks": _("由采购订单 {0} 自动生成，付款条件: {1}").format(
                doc.name,
                doc.payment_terms_template or _("自定义"),
            ),
        })
        payment_plan.insert(ignore_permissions=True)
        created_count += 1

    if created_count > 0:
        frappe.msgprint(
            _("已自动生成 {0} 条付款计划记录。").format(created_count),
            alert=True,
        )


def cancel_payment_plans(doc, method):
    """
    Purchase Order on_cancel: 取消关联的付款计划
    """
    plans = frappe.get_all(
        "Payment Plan",
        filters={
            "purchase_order": doc.name,
            "status": ("!=", "Cancelled"),
        },
        pluck="name",
    )

    for plan_name in plans:
        plan = frappe.get_doc("Payment Plan", plan_name)
        plan.status = "Cancelled"
        plan.remarks = _("采购订单 {0} 已取消，关联付款计划自动取消。").format(doc.name)
        plan.save(ignore_permissions=True)

    if plans:
        frappe.msgprint(
            _("已取消 {0} 条关联付款计划。").format(len(plans)),
            alert=True,
        )
