"""月度请假扣款明细报表"""

import frappe
from frappe import _
from frappe.utils import flt, getdate


def execute(filters=None):
    if not filters:
        filters = {}

    columns = get_columns()
    data = get_data(filters)

    total_amount = sum(flt(row.amount) for row in data)
    total_days = sum(flt(row.leave_days) for row in data)
    data.append({
        "employee": "",
        "employee_name": "",
        "leave_type": "",
        "leave_application": "",
        "leave_days": total_days,
        "deduction_rate": "",
        "amount": total_amount,
        "payroll_month": "",
        "remarks": "合计",
        "is_total": True,
    })

    chart = get_chart_data(data[:-1])

    return columns, data, None, chart


def get_columns():
    return [
        {
            "fieldname": "employee",
            "label": _("Employee"),
            "fieldtype": "Link",
            "options": "Employee",
            "width": 120,
        },
        {
            "fieldname": "employee_name",
            "label": _("Employee Name"),
            "fieldtype": "Data",
            "width": 150,
        },
        {
            "fieldname": "leave_type",
            "label": _("Leave Type"),
            "fieldtype": "Link",
            "options": "Leave Type",
            "width": 120,
        },
        {
            "fieldname": "leave_application",
            "label": _("Leave Application"),
            "fieldtype": "Link",
            "options": "Leave Application",
            "width": 160,
        },
        {
            "fieldname": "leave_days",
            "label": _("Leave Days"),
            "fieldtype": "Float",
            "width": 90,
        },
        {
            "fieldname": "deduction_rate",
            "label": _("Deduction Rate"),
            "fieldtype": "Percent",
            "width": 90,
        },
        {
            "fieldname": "amount",
            "label": _("Deduction Amount"),
            "fieldtype": "Currency",
            "width": 120,
        },
        {
            "fieldname": "payroll_month",
            "label": _("Payroll Month"),
            "fieldtype": "Date",
            "width": 100,
        },
        {
            "fieldname": "remarks",
            "label": _("Remarks"),
            "fieldtype": "Data",
            "width": 200,
        },
    ]


def get_data(filters):
    payroll_month = filters.get("payroll_month")
    employee = filters.get("employee")

    conditions = []
    if payroll_month:
        conditions.append(
            "DATE_FORMAT(ed.payroll_month, '%%Y-%%m') = DATE_FORMAT(%(payroll_month)s, '%%Y-%%m')"
        )
    if employee:
        conditions.append("ed.employee = %(employee)s")

    where = " AND ".join(conditions) if conditions else "1=1"

    return frappe.db.sql(
        f"""
        SELECT
            ed.employee,
            ed.employee_name,
            ed.leave_type,
            ed.leave_application,
            ed.leave_days,
            ed.deduction_rate,
            ed.deduction_amount AS amount,
            ed.payroll_month,
            ed.remarks
        FROM `tabExtra Deduction` ed
        WHERE {where}
        ORDER BY ed.employee, ed.leave_type
        """,
        {"payroll_month": payroll_month, "employee": employee},
        as_dict=True,
    )


def get_chart_data(data):
    if not data:
        return None

    employee_totals = {}
    for row in data:
        emp = row["employee"] or _("Unknown")
        employee_totals[emp] = employee_totals.get(emp, 0) + (row["amount"] or 0)

    labels = list(employee_totals.keys())
    values = list(employee_totals.values())

    return {
        "data": {
            "labels": labels,
            "datasets": [{"name": _("Deduction Amount"), "values": values}],
        },
        "type": "bar",
    }
