frappe.query_reports["Fees Due"] = {
	filters: [
		{ fieldname: "until", label: __("Due Until"), fieldtype: "Date", default: frappe.datetime.add_days(frappe.datetime.get_today(), 30) },
		{ fieldname: "institution", label: __("Institution"), fieldtype: "Link", options: "Education Institution" },
		{ fieldname: "grade_level", label: __("Grade or Year"), fieldtype: "Link", options: "Grade Level" },
	],
};
