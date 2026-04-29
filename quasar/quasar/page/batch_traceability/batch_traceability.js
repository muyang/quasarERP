frappe.pages["batch-traceability"].on_page_load = function (wrapper) {
	var page = frappe.ui.make_app_page({
		parent: wrapper,
		title: __("批次追溯看板"),
		single_column: false,
	});

	frappe.breadcrumbs.add("Stock");

	$(frappe.render_template("batch_traceability", {})).appendTo(page.body);

	// Enter key triggers search
	page.body.find('[data-fieldname="batch_no"]').on("keypress", function (e) {
		if (e.which === 13) {
			search_batch(page);
		}
	});

	page.set_primary_action(__("查询追溯"), function () {
		search_batch(page);
	});

	page.add_inner_button(__("导出 PDF"), function () {
		export_pdf(page);
	});
};

function search_batch(page) {
	var batch_no = page.body.find('[data-fieldname="batch_no"]').val().trim();
	if (!batch_no) {
		frappe.msgprint({ title: __("提示"), message: __("请输入批次号"), indicator: "orange" });
		return;
	}

	frappe.call({
		method: "quasar.quasar.page.batch_traceability.batch_traceability.get_batch_traceability",
		args: { batch_no: batch_no },
		btn: page.body.find(".btn-search"),
		callback: function (r) {
			render_results(page, r.message);
		},
	});
}

function render_results(page, data) {
	var $results = page.body.find(".traceability-results");
	$results.empty();

	if (!data || (!data.upstream.length && !data.downstream.length)) {
		$results.html(
			'<div class="text-muted text-center" style="padding: 40px;">' +
			__("未找到该批次的追溯记录") +
			"</div>"
		);
		return;
	}

	// Upstream section
	if (data.upstream.length) {
		$results.append('<h5 class="mt-4">' + __("🔺 向上追溯 — 来源") + "</h5>");
		render_timeline($results, data.upstream, "upstream");
	}

	// Downstream section
	if (data.downstream.length) {
		$results.append('<h5 class="mt-4">' + __("🔻 向下追溯 — 去向") + "</h5>");
		render_timeline($results, data.downstream, "downstream");
	}
}

function render_timeline($container, entries, direction) {
	var $list = $('<div class="trace-timeline"></div>');

	entries.forEach(function (entry) {
		var item = $(frappe.render_template("batch_traceability_item", {
			direction: direction,
			posting_date: entry.posting_date,
			voucher_type: entry.voucher_type,
			voucher_no: entry.voucher_no,
			voucher_url: entry.voucher_url,
			item_code: entry.item_code,
			item_name: entry.item_name,
			actual_qty: entry.actual_qty,
			warehouse: entry.warehouse,
		}));
		$list.append(item);
	});

	$container.append($list);
}

function export_pdf(page) {
	var batch_no = page.body.find('[data-fieldname="batch_no"]').val().trim();
	if (!batch_no) {
		frappe.msgprint({ title: __("提示"), message: __("请先输入批次号"), indicator: "orange" });
		return;
	}

	var print_w = window.open(
		"/api/method/quasar.quasar.page.batch_traceability.batch_traceability.get_batch_traceability"
		+ "?batch_no=" + encodeURIComponent(batch_no),
		"_blank"
	);
	print_w.onload = function () { print_w.print(); };
}
