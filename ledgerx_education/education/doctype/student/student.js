frappe.ui.form.on("Student", {
	setup(frm) {
		frm.set_query("section", () => ({ filters: { grade_level: frm.doc.grade_level, academic_year: frm.doc.academic_year } }));
		frm.set_query("guardian", "guardians", () => ({}));
	},
	grade_level(frm) { if (frm.doc.section) frm.set_value("section", ""); },
	academic_year(frm) { if (frm.doc.section) frm.set_value("section", ""); },
	onload(frm) {
		if (frm.is_new() && !frm.doc.academic_year) {
			frappe.db.get_value("Academic Year", { is_current: 1 }, "name").then((r) => r.message && r.message.name && frm.set_value("academic_year", r.message.name));
		}
	},
	refresh(frm) {
		if (frm.is_new()) return;
		frm.add_custom_button(__("New Fees"), () => frappe.new_doc("Student Fee", { student: frm.doc.name, academic_year: frm.doc.academic_year }), __("Create"));
		frm.add_custom_button(__("Course Registration"), () => frappe.new_doc("Course Registration", { student: frm.doc.name, academic_year: frm.doc.academic_year }), __("Create"));
		frm.add_custom_button(__("Fees"), () => frappe.set_route("List", "Student Fee", { student: frm.doc.name }), __("View"));
		frm.add_custom_button(__("Report Card"), () => frappe.set_route("query-report", "Student Report Card", { student: frm.doc.name }), __("View"));
	},
});
