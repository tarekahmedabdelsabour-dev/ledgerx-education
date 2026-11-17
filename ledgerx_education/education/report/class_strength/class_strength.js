frappe.query_reports["Class Strength"] = {
	filters: [
		{ fieldname: "academic_year", label: __("Academic Year"), fieldtype: "Link", options: "Academic Year" },
		{ fieldname: "grade_level", label: __("Grade or Year"), fieldtype: "Link", options: "Grade Level" },
	],
};
