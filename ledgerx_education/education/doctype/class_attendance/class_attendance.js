frappe.ui.form.on("Class Attendance", {
	setup(frm) {
		frm.set_query("course_offering", () => ({ filters: { section: frm.doc.section } }));
	},
	refresh(frm) {
		if (frm.is_new() && !frm.doc.students.length && frm.doc.section) frm.events.load(frm);
		frm.add_custom_button(__("Load the Class"), () => frm.events.load(frm), __("Students"));
		frm.add_custom_button(__("Everyone Present"), () => { (frm.doc.students || []).forEach((r) => frappe.model.set_value(r.doctype, r.name, "status", "Present")); }, __("Students"));
	},
	section(frm) { if (frm.doc.section) frm.events.load(frm); },
	load(frm) {
		if (!frm.doc.section) return;
		frappe.call({ method: "frappe.client.get_list", args: { doctype: "Student", filters: { section: frm.doc.section, status: "Active" }, fields: ["name"], order_by: "student_name", limit_page_length: 500 } })
			.then((r) => {
				const have = new Set((frm.doc.students || []).map((x) => x.student));
				(r.message || []).forEach((s) => { if (!have.has(s.name)) frm.add_child("students", { student: s.name, status: "Present" }); });
				frm.refresh_field("students");
			});
	},
});
