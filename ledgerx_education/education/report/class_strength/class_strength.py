import frappe
from frappe import _


def execute(filters=None):
	filters = filters or {}
	f = {}
	for k in ("academic_year", "grade_level"):
		if filters.get(k):
			f[k] = filters[k]
	rows = frappe.get_all("Class Section", filters=f, fields=["name", "grade_level", "section_name", "academic_year", "capacity", "homeroom_teacher", "room"],
		order_by="grade_level, section_name")
	counts = dict(frappe.db.sql("select section, count(*) from `tabStudent` where status = 'Active' and ifnull(section, '') != '' group by section"))
	for r in rows:
		r["students"] = counts.get(r.name, 0)
		r["free"] = (r.capacity or 0) - r["students"]
	cols = [
		{"label": _("Section"), "fieldname": "name", "fieldtype": "Link", "options": "Class Section", "width": 200},
		{"label": _("Grade or Year"), "fieldname": "grade_level", "fieldtype": "Link", "options": "Grade Level", "width": 150},
		{"label": _("Academic Year"), "fieldname": "academic_year", "fieldtype": "Link", "options": "Academic Year", "width": 110},
		{"label": _("Class Teacher"), "fieldname": "homeroom_teacher", "fieldtype": "Link", "options": "Employee", "width": 140},
		{"label": _("Capacity"), "fieldname": "capacity", "fieldtype": "Int", "width": 80},
		{"label": _("Students"), "fieldname": "students", "fieldtype": "Int", "width": 80},
		{"label": _("Free Seats"), "fieldname": "free", "fieldtype": "Int", "width": 90},
	]
	return cols, rows
