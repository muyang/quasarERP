"""付款计划 DocType 控制器"""

import frappe
from frappe.model.document import Document


class PaymentPlan(Document):
    """付款计划 — 由采购订单提交时自动生成"""

    # begin: auto-generated types
    # This code is auto-generated. Do not modify anything in this block.

    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amended_from: DF.Link | None
        amount: DF.Currency
        is_paid: DF.Check
        paid_date: DF.Date | None
        planned_payment_date: DF.Date
        posting_date: DF.Date | None
        purchase_order: DF.Link
        remarks: DF.SmallText | None
        status: DF.Literal["Pending", "Paid", "Cancelled"]
        supplier: DF.Link
        supplier_name: DF.Data | None
    # end: auto-generated types

    def validate(self):
        if self.is_paid and not self.paid_date:
            self.paid_date = frappe.utils.today()
        if self.is_paid:
            self.status = "Paid"
        elif self.status == "Cancelled":
            pass
        else:
            self.status = "Pending"
