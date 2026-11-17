import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt


class CourseRegistration(Document):
	def validate(self):
		seen = set()
		for r in self.items:
			if r.course_offering in seen:
				frappe.throw(_("Row {0}: the course is listed twice").format(r.idx))
			seen.add(r.course_offering)
			o = frappe.db.get_value("Course Offering", r.course_offering, ["status", "academic_year"], as_dict=True)
			if o.status != "Open":
				frappe.throw(_("Row {0}: the course is closed").format(r.idx))
			if o.academic_year != self.academic_year:
				frappe.throw(_("Row {0}: the course is in another academic year").format(r.idx))
		self.total_credit_hours = sum(flt(frappe.db.get_value("Subject", frappe.db.get_value("Course Offering", r.course_offering, "subject"), "credit_hours"))
			for r in self.items)
		if frappe.db.exists("Course Registration", {"student": self.student, "academic_year": self.academic_year, "term_name": self.term_name,
				"status": ["!=", "Cancelled"], "name": ["!=", self.name or ""]}):
			frappe.throw(_("The student is already registered for this term"))

	@frappe.whitelist()
	def confirm(self):
		if self.status != "Draft":
			frappe.throw(_("The registration is {0}").format(_(self.status)))
		for r in self.items:
			cap = frappe.db.get_value("Course Offering", r.course_offering, "capacity")
			if cap:
				taken = frappe.db.sql("""select count(*) from `tabCourse Registration Item` i join `tabCourse Registration` r on r.name = i.parent
					where i.course_offering = %s and r.status = 'Confirmed'""", r.course_offering)[0][0]
				if taken >= cap:
					frappe.throw(_("Row {0}: the course is full ({1})").format(r.idx, cap))
		self.db_set("status", "Confirmed")

	@frappe.whitelist()
	def cancel_registration(self):
		self.db_set("status", "Cancelled")
