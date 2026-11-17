frappe.query_reports["Fee Collection"] = {
	filters: [
		{ fieldname: "academic_year", label: __("Academic Year"), fieldtype: "Link", options: "Academic Year" },
		{ fieldname: "institution", label: __("Institution"), fieldtype: "Link", options: "Education Institution" },
	],
};
