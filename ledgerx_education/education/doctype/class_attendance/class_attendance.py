import frappe
from frappe import _
from frappe.model.document import Document


class ClassAttendance(Document):
	def validate(self):
		if frappe.db.sql("""select name from `tabClass Attendance` where attendance_date = %s and section = %s and ifnull(course_offering, '') = %s
				and name != %s limit 1""", (self.attendance_date, self.section, self.course_offering or "", self.name or "")):
			frappe.throw(_("The attendance of this class on this day is already taken"))
		seen = set()
		for r in self.students:
			if r.student in seen:
				frappe.throw(_("Row {0}: {1} is listed twice").format(r.idx, r.student))
			seen.add(r.student)
		c = lambda s: sum(1 for r in self.students if r.status == s)
		self.present_count, self.late_count, self.absent_count = c("Present"), c("Late"), c("Absent")

	@frappe.whitelist()
	def load_students(self):
		have = {r.student for r in self.students}
		for s in frappe.get_all("Student", filters={"section": self.section, "status": "Active"}, pluck="name", order_by="student_name"):
			if s not in have:
				self.append("students", {"student": s, "status": "Present"})
		return len(self.students)
