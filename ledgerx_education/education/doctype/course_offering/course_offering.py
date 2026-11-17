import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_time


class CourseOffering(Document):
	def validate(self):
		self.title = f"{self.subject} - {self.section or self.grade_level or _('Open registration')} ({self.academic_year})"
		for r in self.schedule:
			if get_time(r.to_time) <= get_time(r.from_time):
				frappe.throw(_("Row {0}: the class ends before it starts").format(r.idx))
		if self.teacher:
			self._teacher_clash()

	def _teacher_clash(self):
		"""The same teacher cannot be in two classes at the same hour of the same day."""
		for r in self.schedule:
			clash = frappe.db.sql(
				"""select o.name from `tabCourse Offering` o join `tabCourse Schedule Slot` s on s.parent = o.name
				where o.teacher = %s and o.name != %s and o.academic_year = %s and o.status = 'Open' and s.day = %s
				and s.from_time < %s and s.to_time > %s limit 1""",
				(self.teacher, self.name or "", self.academic_year, r.day, r.to_time, r.from_time))
			if clash:
				frappe.throw(_("Row {0}: the teacher already has a class on {1} at that time ({2})").format(r.idx, _(r.day), clash[0][0]))
