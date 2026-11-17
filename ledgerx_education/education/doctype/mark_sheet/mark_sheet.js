frappe.ui.form.on("Mark Sheet", {
	refresh(frm) {
		frm.add_custom_button(__("Load the Students"), () => frm.call({ doc: frm.doc, method: "load_students", freeze: true }).then(() => frm.refresh()), __("Students"));
		if (frm.doc.status === "Draft" && !frm.is_new()) frm.add_custom_button(__("Publish the Marks"), () => frm.set_value("status", "Published").then(() => frm.save()));
	},
	course_offering(frm) {
		if (frm.is_new() && frm.doc.course_offering && !(frm.doc.students || []).length)
			frm.call({ doc: frm.doc, method: "load_students" }).then(() => frm.refresh_field("students"));
	},
});
