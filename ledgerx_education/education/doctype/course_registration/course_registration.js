frappe.ui.form.on("Course Registration", {
	setup(frm) {
		frm.set_query("course_offering", "items", () => ({ filters: { academic_year: frm.doc.academic_year, status: "Open" } }));
	},
	refresh(frm) {
		if (frm.is_new()) return;
		const act = (method) => frm.call({ doc: frm.doc, method, freeze: true }).then(() => frm.reload_doc());
		if (frm.doc.status === "Draft") frm.add_custom_button(__("Confirm the Registration"), () => act("confirm")).addClass("btn-primary");
		if (frm.doc.status !== "Cancelled") frm.add_custom_button(__("Cancel Registration"), () => frappe.confirm(__("Cancel this registration?"), () => act("cancel_registration")), __("More"));
	},
});
