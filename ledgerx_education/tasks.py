import frappe
from frappe import _
from frappe.utils import add_days, nowdate


def absence_alerts():
	"""Daily: a student with many absences in the last 30 days becomes a to-do for the class teacher."""
	limit = int(frappe.get_cached_doc("Education Settings").absence_alert or 0)
	if limit <= 0:
		return
	rows = frappe.db.sql(
		"""select s.student, s.student_name, a.section, count(*) as n from `tabClass Attendance Student` s join `tabClass Attendance` a on a.name = s.parent
		where s.status = 'Absent' and ifnull(a.course_offering, '') = '' and a.attendance_date between %s and %s group by s.student, s.student_name, a.section
		having count(*) >= %s""", (add_days(nowdate(), -30), nowdate(), limit), as_dict=True)
	for r in rows:
		teacher = frappe.db.get_value("Class Section", r.section, "homeroom_teacher")
		user = frappe.db.get_value("Employee", teacher, "user_id") if teacher else None
		if not user or frappe.db.exists("ToDo", {"reference_type": "Student", "reference_name": r.student, "status": "Open", "allocated_to": user}):
			continue
		try:
			frappe.get_doc({"doctype": "ToDo", "allocated_to": user, "reference_type": "Student", "reference_name": r.student, "priority": "High",
				"description": _("{0} was absent {1} times in the last 30 days: contact the guardian").format(r.student_name, r.n)}).insert(ignore_permissions=True)
			frappe.db.commit()
		except Exception:
			frappe.db.rollback()
			frappe.log_error(title=f"Education absence alert failed for {r.student}")
