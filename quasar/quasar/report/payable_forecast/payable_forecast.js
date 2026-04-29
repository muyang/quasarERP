frappe.query_reports["Payable Forecast"] = {
    "filters": [
        {
            "fieldname": "days_ahead",
            "label": __("未来天数"),
            "fieldtype": "Int",
            "default": 30,
            "reqd": 1,
        },
        {
            "fieldname": "supplier",
            "label": __("供应商"),
            "fieldtype": "Link",
            "options": "Supplier",
        },
    ],
    "onload": function (report) {
        // 默认按供应商分组
    },
};
