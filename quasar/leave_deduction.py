"""请假扣款模块

- Leave Application on_submit: 对标记为扣款的请假类型生成 Extra Deduction 记录
- 提供 Salary Structure 公式中调用的当月扣款查询函数
"""

import frappe
from frappe import _
from frappe.utils import flt, getdate, get_first_day, get_last_day, month_diff


def create_extra_deduction(doc, method):
    """
    Leave Application on_submit:
    若请假类型的 custom_is_deductible 勾选，自动生成 Extra Deduction
    """
    leave_type_doc = frappe.get_cached_doc("Leave Type", doc.leave_type)

    if not leave_type_doc.custom_is_deductible:
        return

    deduction_rate = flt(leave_type_doc.custom_deduction_rate or 100)
    leave_days = flt(doc.total_leave_days)

    if leave_days <= 0:
        return

    # 确定扣款归属月（取请假开始日期所在月）
    payroll_month = get_first_day(doc.from_date)

    # 检查是否已存在相同请假单的扣款记录
    existing = frappe.db.exists(
        "Extra Deduction", {"leave_application": doc.name}
    )
    if existing:
        return

    deduction = frappe.get_doc({
        "doctype": "Extra Deduction",
        "employee": doc.employee,
        "leave_application": doc.name,
        "leave_type": doc.leave_type,
        "posting_date": frappe.utils.today(),
        "payroll_month": payroll_month,
        "leave_days": leave_days,
        "deduction_rate": deduction_rate,
        "deduction_amount": 0,  # 实际扣款金额由薪资公式计算
        "remarks": _("由请假单 {0} 自动生成").format(doc.name),
    })
    deduction.insert(ignore_permissions=True)


@frappe.whitelist()
def get_monthly_deduction(employee, payroll_month):
    """获取员工指定月份的请假扣款汇总，供 Salary Structure 公式调用"""
    total = frappe.db.sql(
        """
        SELECT COALESCE(SUM(deduction_amount), 0)
        FROM `tabExtra Deduction`
        WHERE employee = %s
          AND DATE_FORMAT(payroll_month, '%%Y-%%m') = DATE_FORMAT(%s, '%%Y-%%m')
        """,
        (employee, payroll_month),
    )[0][0]

    return flt(total)


@frappe.whitelist()
def get_deductible_leave_days(employee, payroll_month):
    """获取员工指定月份的扣款请假天数汇总"""
    total = frappe.db.sql(
        """
        SELECT COALESCE(SUM(leave_days), 0)
        FROM `tabExtra Deduction`
        WHERE employee = %s
          AND DATE_FORMAT(payroll_month, '%%Y-%%m') = DATE_FORMAT(%s, '%%Y-%%m')
        """,
        (employee, payroll_month),
    )[0][0]

    return flt(total)
