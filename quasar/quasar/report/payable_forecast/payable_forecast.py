"""
应付账款未来 N 天预测报表 (Script Report)

按供应商和日期分组，展示未来指定天数内的应付计划。
"""

import frappe
from frappe import _
from frappe.utils import add_days, getdate, today


def execute(filters=None):
    """Script Report 入口"""
    if not filters:
        filters = {}

    days_ahead = int(filters.get("days_ahead", 30))
    from_date = filters.get("from_date") or today()
    to_date = filters.get("to_date") or add_days(today(), days_ahead)

    columns = get_columns()
    data = get_data(filters, from_date, to_date)

    # Summary row
    total = sum(row.amount for row in data if row.amount)
    data.append({
        "supplier": "",
        "purchase_order": "",
        "planned_payment_date": "",
        "amount": total,
        "days_until_due": "",
        "status": "合计",
        "remarks": "",
        "is_total": True,
    })

    chart = get_chart_data(data[:-1])

    return columns, data, None, chart


def get_columns():
    return [
        {
            "fieldname": "supplier",
            "label": _("供应商"),
            "fieldtype": "Link",
            "options": "Supplier",
            "width": 150,
        },
        {
            "fieldname": "purchase_order",
            "label": _("采购订单"),
            "fieldtype": "Link",
            "options": "Purchase Order",
            "width": 150,
        },
        {
            "fieldname": "planned_payment_date",
            "label": _("计划付款日期"),
            "fieldtype": "Date",
            "width": 120,
        },
        {
            "fieldname": "amount",
            "label": _("金额"),
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "fieldname": "days_until_due",
            "label": _("距今天数"),
            "fieldtype": "Int",
            "width": 100,
        },
        {
            "fieldname": "status",
            "label": _("状态"),
            "fieldtype": "Data",
            "width": 100,
        },
        {
            "fieldname": "remarks",
            "label": _("备注"),
            "fieldtype": "Data",
            "width": 250,
        },
    ]


def get_data(filters, from_date, to_date):
    """查询付款计划数据"""
    conditions = [
        "plan.status = 'Pending'",
        f"plan.planned_payment_date >= '{getdate(from_date)}'",
        f"plan.planned_payment_date <= '{getdate(to_date)}'",
    ]

    if filters.get("supplier"):
        conditions.append(f"plan.supplier = '{filters['supplier']}'")

    where_clause = " AND ".join(conditions)

    data = frappe.db.sql(
        f"""
        SELECT
            plan.supplier,
            plan.purchase_order,
            plan.planned_payment_date,
            plan.amount,
            DATEDIFF(plan.planned_payment_date, CURDATE()) AS days_until_due,
            plan.status,
            plan.remarks
        FROM `tabPayment Plan` plan
        WHERE {where_clause}
        ORDER BY plan.planned_payment_date ASC, plan.supplier
        """,
        as_dict=True,
    )

    return data


def get_chart_data(data):
    """生成按供应商汇总的图表数据"""
    if not data:
        return None

    supplier_totals = {}
    for row in data:
        supplier = row["supplier"] or _("未知供应商")
        supplier_totals[supplier] = supplier_totals.get(supplier, 0) + (row["amount"] or 0)

    labels = list(supplier_totals.keys())
    values = list(supplier_totals.values())

    if len(labels) > 20:
        sorted_items = sorted(supplier_totals.items(), key=lambda x: x[1], reverse=True)[:20]
        labels = [item[0] for item in sorted_items]
        values = [item[1] for item in sorted_items]

    return {
        "data": {
            "labels": labels,
            "datasets": [{"name": _("应付金额"), "values": values}],
        },
        "type": "bar",
    }
