frappe.ui.form.on("Student Fee", {
	setup(frm) {
		frm.set_query("fee_structure", () => ({ filters: { academic_year: frm.doc.academic_year, active: 1 } }));
	},
	onload(frm) {
		if (frm.is_new() && !frm.doc.first_due_date) frm.set_value("first_due_date", frappe.datetime.get_today());
	},
	show_schedule(frm) {
		const w = frm.fields_dict.schedule_html && frm.fields_dict.schedule_html.$wrapper;
		if (!w) return;
		if (!frm.doc.sales_invoice) { w.html(`<p class="text-muted">${__("The schedule appears once the fees are invoiced.")}</p>`); return; }
		frappe.db.get_doc("Sales Invoice", frm.doc.sales_invoice).then((inv) => {
			const today = frappe.datetime.get_today();
			const rows = (inv.payment_schedule || []).map((r) => {
				const due = flt(r.payment_amount) - flt(r.paid_amount);
				const late = due > 0.005 && r.due_date < today;
				return `<tr><td>${frappe.datetime.str_to_user(r.due_date)}</td><td>${format_currency(r.payment_amount)}</td><td>${format_currency(r.paid_amount)}</td>
					<td>${due > 0.005 ? format_currency(due) : "✓"}</td><td>${late ? `<span class="indicator-pill red">${__("Late")}</span>` : ""}</td></tr>`;
			}).join("");
			w.html(`<table class="table table-bordered"><thead><tr><th>${__("Due Date")}</th><th>${__("Amount")}</th><th>${__("Paid")}</th><th>${__("Still Due")}</th><th></th></tr></thead><tbody>${rows}</tbody></table>`);
		});
	},
	refresh(frm) {
		frm.events.show_schedule(frm);
		if (frm.is_new()) return;
		const act = (method, args) => frm.call({ doc: frm.doc, method, args: args || {}, freeze: true }).then(() => frm.reload_doc());
		const ask = (title, fields, method) => {
			const d = new frappe.ui.Dialog({ title, fields, primary_action_label: __("Save"), primary_action(v) { d.hide(); act(method, v); } });
			d.show();
		};
		if (frm.doc.status === "Draft") {
			frm.add_custom_button(__("Invoice the Fees"), () => frappe.confirm(__("Create the invoice and the installments?"), () => act("confirm"))).addClass("btn-primary");
			frm.add_custom_button(__("Add Credit Hour Fees"), () => ask(__("Credit Hours"), [
				{ fieldname: "registration", fieldtype: "Link", options: "Course Registration", label: __("Course Registration"), reqd: 1,
					get_query: () => ({ filters: { student: frm.doc.student, status: "Confirmed" } }) }], "add_credit_hours"), __("More"));
			frm.add_custom_button(__("Cancel Draft"), () => act("cancel_draft"), __("More"));
		}
		if (frm.doc.status === "Invoiced") {
			frm.add_custom_button(__("Issue Credit Note"), () => ask(__("Issue Credit Note"), [
				{ fieldname: "reason", fieldtype: "Small Text", label: __("Reason"), reqd: 1 }], "issue_credit_note"), __("More"));
			frm.add_custom_button(__("Receive Payment"), () => ask(__("Receive Payment"), [
				{ fieldname: "mode_of_payment", fieldtype: "Link", options: "Mode of Payment", label: __("Mode of Payment"), reqd: 1 },
				{ fieldname: "amount", fieldtype: "Currency", label: __("Amount"), reqd: 1 },
				{ fieldname: "reference", fieldtype: "Data", label: __("Reference") }], "receive_payment"), __("Money"));
			frm.add_custom_button(__("Open Invoice"), () => frappe.set_route("Form", "Sales Invoice", frm.doc.sales_invoice));
		}
	},
});
