frappe.ui.form.on("Admission Application", {
	refresh(frm) {
		if (frm.is_new()) return;
		const call = (method, args) => frm.call({ doc: frm.doc, method, args: args || {}, freeze: true }).then((r) => { frm.reload_doc(); return r; });
		const s = frm.doc.status;
		if (s === "Enrolled") {
			if (frm.doc.student) frm.add_custom_button(__("Open Student"), () => frappe.set_route("Form", "Student", frm.doc.student));
			return;
		}
		if (["Rejected", "Withdrawn"].includes(s)) return;
		const setS = (st) => () => call("set_status", { status: st });
		if (s === "New") frm.add_custom_button(__("Under Review"), setS("Under Review"), __("Status"));
		if (["New", "Under Review"].includes(s)) frm.add_custom_button(__("Interview Scheduled"), setS("Interview Scheduled"), __("Status"));
		if (s !== "Accepted") frm.add_custom_button(__("Accept"), setS("Accepted"), __("Status"));
		frm.add_custom_button(__("Reject"), () => frappe.confirm(__("Reject this application?"), setS("Rejected")), __("Status"));
		frm.add_custom_button(__("Withdrawn"), setS("Withdrawn"), __("Status"));
		if (!frm.doc.registration_paid) {
			frm.add_custom_button(__("Receive the Registration Fee"), () => {
				const d = new frappe.ui.Dialog({ title: __("Registration Fee"), fields: [
					{ fieldname: "mode_of_payment", fieldtype: "Link", options: "Mode of Payment", label: __("Mode of Payment"), reqd: 1 },
					{ fieldname: "amount", fieldtype: "Currency", label: __("Amount"), default: frm.doc.registration_fee, reqd: 1 },
					{ fieldname: "reference", fieldtype: "Data", label: __("Reference") }],
					primary_action_label: __("Receive"), primary_action(v) { d.hide(); call("pay_registration", v); } });
				d.show();
			}, __("Money"));
		}
		if (s === "Accepted") {
			frm.add_custom_button(__("Enroll the Student"), () => {
				const d = new frappe.ui.Dialog({ title: __("Enroll"), fields: [
					{ fieldname: "section", fieldtype: "Link", options: "Class Section", label: __("Section"),
						get_query: () => ({ filters: { grade_level: frm.doc.grade_level, academic_year: frm.doc.academic_year } }) }],
					primary_action_label: __("Enroll"), primary_action(v) { d.hide(); call("enroll", v).then((r) => r.message && frappe.set_route("Form", "Student", r.message)); } });
				d.show();
			}).addClass("btn-primary");
		}
	},
});
