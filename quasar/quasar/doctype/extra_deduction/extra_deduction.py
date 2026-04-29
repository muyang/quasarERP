from frappe.model.document import Document


class ExtraDeduction(Document):
    # begin: auto-generated types
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amended_from: DF.Link | None
        deduction_amount: DF.Currency
        deduction_rate: DF.Percent
        employee: DF.Link
        employee_name: DF.Data | None
        leave_application: DF.Link
        leave_days: DF.Float
        leave_type: DF.Link | None
        payroll_month: DF.Date
        posting_date: DF.Date
        remarks: DF.SmallText | None
    # end: auto-generated types

    pass
