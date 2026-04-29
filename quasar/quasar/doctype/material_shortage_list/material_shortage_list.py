"""缺料清单 DocType 控制器"""
import frappe
from frappe.model.document import Document


class MaterialShortageList(Document):
    # begin: auto-generated types
    from typing import TYPE_CHECKING

    if TYPE_CHECKING:
        from frappe.types import DF

        amended_from: DF.Link | None
        items: DF.Table
        posting_date: DF.Date | None
        production_item: DF.Link | None
        status: DF.Literal["待处理", "采购申请已生成", "已解决"]
        work_order: DF.Link
    # end: auto-generated types

    pass
