"""
销售订单信用额度控制模块

功能：
- 当销售订单金额 + 应收账款超过信用额度的 80% 时，弹出预警信息但允许保存
- 当超过 100% 时，只有拥有"超额度审批角色"的用户可以提交
- 完全兼容 ERPNext 现有信用额度体系，通过 override_doctype_class 扩展
"""

import frappe
from frappe import _
from erpnext.selling.doctype.sales_order.sales_order import SalesOrder
from erpnext.selling.doctype.customer.customer import (
    get_credit_limit,
    get_customer_outstanding,
)


class QuasarSalesOrder(SalesOrder):
    """扩展 SalesOrder，增加分级信用额度控制"""

    def check_credit_limit(self):
        """
        覆盖原版 check_credit_limit，实现分级控制：
        - 80%-100%：预警但放行
        - >=100%：无审批角色则禁止提交
        """
        if not self.customer or not self.company:
            return

        # 检查是否在 Customer Credit Limit 中设置了绕过标志
        bypass = frappe.db.get_value(
            "Customer Credit Limit",
            {
                "parent": self.customer,
                "parenttype": "Customer",
                "company": self.company,
                "bypass_credit_limit_check": 1,
            },
        )
        if bypass:
            return

        credit_limit = get_credit_limit(self.customer, self.company)
        if not credit_limit:
            return

        outstanding = get_customer_outstanding(self.customer, self.company)
        current_total = self.grand_total or 0
        total_exposure = outstanding + current_total

        if total_exposure < 0:
            return  # 负值表示客户有预付款或贷方余额，无需检查

        ratio = (total_exposure / credit_limit) * 100

        # 从客户档案获取审批角色
        approval_role = frappe.db.get_value(
            "Customer", self.customer, "custom_over_credit_approval_role"
        )

        if ratio >= 100:
            if approval_role and approval_role in frappe.get_roles():
                # 拥有审批角色的用户：允许提交但记录警告
                frappe.msgprint(
                    _(
                        "客户 <b>{0}</b> 信用额度已超出！<br>"
                        "应收账款: {1}<br>"
                        "本次订单: {2}<br>"
                        "信用额度: {3}<br>"
                        "使用率: {4:.1f}%<br><br>"
                        "已以审批角色 <b>{5}</b> 身份通过。"
                    ).format(
                        self.customer,
                        frappe.utils.fmt_money(outstanding, currency=self.currency),
                        frappe.utils.fmt_money(
                            current_total, currency=self.currency
                        ),
                        frappe.utils.fmt_money(credit_limit, currency=self.currency),
                        ratio,
                        approval_role,
                    ),
                    title=_("超额度审批"),
                    indicator="orange",
                )
            else:
                # 无审批角色：禁止提交
                role_msg = (
                    _("此订单需要由 <b>{0}</b> 角色审批后才能提交。").format(
                        approval_role
                    )
                    if approval_role
                    else _("且未指定超额度审批角色。请联系管理员配置。")
                )

                frappe.throw(
                    _(
                        "客户 <b>{0}</b> 信用额度已超出！<br>"
                        "应收账款: {1}<br>"
                        "本次订单: {2}<br>"
                        "信用额度: {3}<br>"
                        "使用率: {4:.1f}%<br><br>"
                        "{5}"
                    ).format(
                        self.customer,
                        frappe.utils.fmt_money(outstanding, currency=self.currency),
                        frappe.utils.fmt_money(
                            current_total, currency=self.currency
                        ),
                        frappe.utils.fmt_money(credit_limit, currency=self.currency),
                        ratio,
                        role_msg,
                    ),
                    title=_("信用额度超标"),
                )

        elif ratio >= 80:
            # 预警但允许提交
            frappe.msgprint(
                _(
                    "客户 <b>{0}</b> 信用额度使用率已达 {1:.1f}%。<br>"
                    "应收账款: {2}<br>"
                    "本次订单: {3}<br>"
                    "信用额度: {4}<br><br>"
                    "<b>请确认是否继续提交此订单。</b>"
                ).format(
                    self.customer,
                    ratio,
                    frappe.utils.fmt_money(outstanding, currency=self.currency),
                    frappe.utils.fmt_money(current_total, currency=self.currency),
                    frappe.utils.fmt_money(credit_limit, currency=self.currency),
                ),
                title=_("信用额度预警"),
                indicator="orange",
            )
