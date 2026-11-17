import frappe
from frappe import _
from frappe.utils import add_days, nowdate

from ledgerx_education.engine import logic


def execute(filters=None):
	filters = filters or {}
	args = [filters.get("from_date") or add_days(nowdate(), -29), filters.get("to_date") or nowdate()]
	cond = ""
	if filters.get("section"):
		cond = " and a.section = %s"
		args.append(filters["section"])
	rows = frappe.db.sql(
		f"""select s.student, s.student_name, a.section,
		sum(s.status = 'Present') as present, sum(s.status = 'Late') as late, sum(s.status = 'Absent') as absent, sum(s.status = 'Excused') as excused
		from `tabClass Attendance Student` s join `tabClass Attendance` a on a.name = s.parent
		where a.attendance_date between %s and %s and ifnull(a.course_offering, '') = '' {cond}
		group by s.student, s.student_name, a.section order by absent desc, s.student_name""", args, as_dict=True)
	for r in rows:
		r["rate"] = logic.attendance_rate(int(r.present or 0), int(r.late or 0), int(r.absent or 0))
	cols = [
		{"label": _("Student"), "fieldname": "student", "fieldtype": "Link", "options": "Student", "width": 120},
		{"label": _("Name"), "fieldname": "student_name", "fieldtype": "Data", "width": 180},
		{"label": _("Section"), "fieldname": "section", "fieldtype": "Link", "options": "Class Section", "width": 160},
		{"label": _("Present"), "fieldname": "present", "fieldtype": "Int", "width": 80},
		{"label": _("Late"), "fieldname": "late", "fieldtype": "Int", "width": 70},
		{"label": _("Absent"), "fieldname": "absent", "fieldtype": "Int", "width": 80},
		{"label": _("Excused"), "fieldname": "excused", "fieldtype": "Int", "width": 80},
		{"label": _("Attendance (%)"), "fieldname": "rate", "fieldtype": "Percent", "width": 110},
	]
	return cols, rows
