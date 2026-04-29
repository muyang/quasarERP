"""批次追溯看板 Page Controller"""

import frappe


@frappe.whitelist()
def get_batch_traceability(batch_no):
    """Query the full traceability chain for a batch/serial number"""
    return {
        "upstream": _trace_upstream(batch_no),
        "downstream": _trace_downstream(batch_no),
    }


def _trace_upstream(batch_no):
    """Trace where this batch came from (purchase receipt, stock entry, etc.)"""
    entries = frappe.db.sql(
        """
        SELECT
            sle.name,
            sle.posting_date,
            sle.posting_time,
            sle.voucher_type,
            sle.voucher_no,
            sle.item_code,
            sle.item_name,
            sle.actual_qty,
            sle.warehouse,
            sle.stock_value_difference
        FROM `tabStock Ledger Entry` sle
        WHERE sle.batch_no = %s
          AND sle.actual_qty > 0
        ORDER BY sle.posting_date ASC, sle.posting_time ASC, sle.creation ASC
        """,
        batch_no,
        as_dict=True,
    )

    # Enrich with voucher links
    for entry in entries:
        entry["voucher_url"] = f"/app/{entry['voucher_type'].lower().replace(' ', '-')}/{entry['voucher_no']}"

    return entries


def _trace_downstream(batch_no):
    """Trace where this batch was consumed/shipped"""
    entries = frappe.db.sql(
        """
        SELECT
            sle.name,
            sle.posting_date,
            sle.posting_time,
            sle.voucher_type,
            sle.voucher_no,
            sle.item_code,
            sle.item_name,
            sle.actual_qty,
            sle.warehouse,
            sle.stock_value_difference
        FROM `tabStock Ledger Entry` sle
        WHERE sle.batch_no = %s
          AND sle.actual_qty < 0
        ORDER BY sle.posting_date ASC, sle.posting_time ASC, sle.creation ASC
        """,
        batch_no,
        as_dict=True,
    )

    for entry in entries:
        entry["actual_qty"] = abs(entry["actual_qty"])
        entry["voucher_url"] = f"/app/{entry['voucher_type'].lower().replace(' ', '-')}/{entry['voucher_no']}"

    return entries
