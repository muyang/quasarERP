// Material Shortage List 客户端脚本 —— 添加"一键生成采购申请"按钮

frappe.ui.form.on("Material Shortage List", {
    refresh: function (frm) {
        if (frm.doc.docstatus === 0 && frm.doc.status === "待处理") {
            frm.add_custom_button(__("一键生成采购申请"), function () {
                frappe.confirm(
                    __("确认根据缺料清单生成采购申请（Material Request）？"),
                    function () {
                        frappe.call({
                            method: "quasar.material_shortage.generate_purchase_request",
                            args: {
                                docname: frm.doc.name,
                            },
                            callback: function (r) {
                                if (!r.exc) {
                                    frm.reload_doc();
                                }
                            },
                            freeze: true,
                            freeze_message: __("生成采购申请中..."),
                        });
                    }
                );
            }, __("操作"));
        }
    },
});
