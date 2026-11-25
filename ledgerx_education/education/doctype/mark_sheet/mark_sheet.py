import frappe
from frappe import _
from frappe.model.document import Document


def students_of_offering(offering):
	"""The students of a class (the section) or, for a course students register for, those registered in it."""
	o = frappe.db.get_value("Course Offering", offering, ["section"], as_dict=True)
	if o.section:
		return frappe.get_all("Student", filters={"section": o.section, "status": "Active"}, pluck="name", order_by="student_name")
	return frappe.db.sql_list(
		"""select distinct r.student from `tabCourse Registration` r join `tabCourse Registration Item` i on i.parent = r.name
		where r.status = 'Confirmed' and i.course_offering = %s""", offering)


class MarkSheet(Document):
	def validate(self):
		self.title = f"{self.course_offering} - {_(self.assessment_type)}"
		if self.max_marks <= 0:
			frappe.throw(_("The maximum marks must be above zero"))
		seen = set()
		for r in self.students:
			if r.student in seen:
				frappe.throw(_("Row {0}: {1} is listed twice").format(r.idx, r.student))
			seen.add(r.student)
			if r.absent:
				r.marks = None
			elif r.marks is not None and not 0 <= r.marks <= self.max_marks:
				frappe.throw(_("Row {0}: marks must be between 0 and {1}").format(r.idx, self.max_marks))

	@frappe.whitelist(methods=["POST"])
	def load_students(self):
		self.check_permission("write")
		have = {r.student for r in self.students}
		for s in students_of_offering(self.course_offering):
			if s not in have:
				self.append("students", {"student": s})
		return len(self.students)
