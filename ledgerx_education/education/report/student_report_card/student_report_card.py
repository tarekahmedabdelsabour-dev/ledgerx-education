import frappe
from frappe import _

from ledgerx_education.engine import logic


def execute(filters=None):
	"""One row per course: the weighted result of the published marks and its grade on the default grading scale."""
	filters = filters or {}
	if not filters.get("student"):
		return [], []
	s = frappe.get_cached_doc("Education Settings")
	scale = []
	if s.grading_scale:
		scale = [(r.from_percent, r.grade, r.points) for r in frappe.get_doc("Grading Scale", s.grading_scale).ranges]
	args = [filters["student"]]
	cond = ""
	if filters.get("academic_year"):
		cond = " and o.academic_year = %s"
		args.append(filters["academic_year"])
	data = frappe.db.sql(
		f"""select o.name as offering, o.subject, o.academic_year, o.teacher, m.max_marks, m.weight, r.marks
		from `tabMark Sheet Student` r join `tabMark Sheet` m on m.name = r.parent join `tabCourse Offering` o on o.name = m.course_offering
		where r.student = %s and m.status = 'Published' {cond} order by o.academic_year, o.subject""", args, as_dict=True)
	by = {}
	for d in data:
		by.setdefault(d.offering, {"subject": d.subject, "academic_year": d.academic_year, "teacher": d.teacher, "items": []})["items"].append(
			(None if d.marks is None else d.marks, d.max_marks, d.weight))
	rows = []
	for o, v in by.items():
		pct = logic.weighted_percent(v["items"])
		grade, points = logic.grade_for(pct, scale) if scale else (None, 0)
		rows.append({"academic_year": v["academic_year"], "subject": v["subject"], "teacher": v["teacher"], "percent": pct, "grade": grade, "points": points,
			"result": _("Pass") if pct >= (s.pass_percent or 0) else _("Fail")})
	cols = [
		{"label": _("Academic Year"), "fieldname": "academic_year", "fieldtype": "Link", "options": "Academic Year", "width": 110},
		{"label": _("Subject"), "fieldname": "subject", "fieldtype": "Link", "options": "Subject", "width": 180},
		{"label": _("Teacher"), "fieldname": "teacher", "fieldtype": "Link", "options": "Employee", "width": 140},
		{"label": _("Result (%)"), "fieldname": "percent", "fieldtype": "Percent", "width": 100},
		{"label": _("Grade"), "fieldname": "grade", "fieldtype": "Data", "width": 70},
		{"label": _("Points"), "fieldname": "points", "fieldtype": "Float", "width": 70},
		{"label": _("Pass or Fail"), "fieldname": "result", "fieldtype": "Data", "width": 90},
	]
	return cols, rows
