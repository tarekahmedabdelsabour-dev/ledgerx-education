frappe.query_reports["Student Report Card"] = {
	filters: [
		{ fieldname: "student", label: __("Student"), fieldtype: "Link", options: "Student", reqd: 1 },
		{ fieldname: "academic_year", label: __("Academic Year"), fieldtype: "Link", options: "Academic Year" },
	],
};
