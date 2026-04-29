"""缺料明细 — 子表 Doctype"""
import frappe
from frappe.model.document import Document


class MaterialShortageItem(Document):
    # begin: auto-generated types
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        available_qty: DF.Float
        item_code: DF.Link
        item_name: DF.Data | None
        purchase_request: DF.Link | None
        required_qty: DF.Float
        shortage_qty: DF.Float
        suggested_supplier: DF.Link | None
        warehouse: DF.Link | None
    # end: auto-generated types

    pass
