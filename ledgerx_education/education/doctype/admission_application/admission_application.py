import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt, nowdate

from ledgerx_education.engine import accounting

STATUSES = ("New", "Under Review", "Interview Scheduled", "Accepted", "Rejected", "Withdrawn")


class AdmissionApplication(Document):
	def validate(self):
		before = self.get_doc_before_save()
		if self.status == "Enrolled" and not self.student:
			frappe.throw(_("Use the Enroll button: it creates the student"))
		if before and before.status == "Enrolled" and self.status != "Enrolled":
			frappe.throw(_("The applicant is already enrolled"))
		if self.interview_date and self.status == "New":
			self.status = "Interview Scheduled"

	@frappe.whitelist()
	def set_status(self, status):
		if status not in STATUSES:
			frappe.throw(_("Choose one of the statuses"))
		if self.status == "Enrolled":
			frappe.throw(_("The applicant is already enrolled"))
		self.db_set("status", status)

	def _guardian(self):
		"""The guardian of this applicant: an existing one (same national ID or phone) or a new one."""
		if self.guardian and frappe.db.exists("Guardian", self.guardian):
			return frappe.get_doc("Guardian", self.guardian)
		found = None
		if self.guardian_national_id:
			found = frappe.db.get_value("Guardian", {"national_id": self.guardian_national_id}, "name")
		if not found:
			found = frappe.db.get_value("Guardian", {"phone": self.guardian_phone}, "name")
		g = frappe.get_doc("Guardian", found) if found else frappe.get_doc({"doctype": "Guardian", "guardian_name": self.guardian_name,
			"phone": self.guardian_phone, "email": self.guardian_email, "national_id": self.guardian_national_id or None}).insert(ignore_permissions=True)
		accounting.ensure_customer(g)
		self.db_set("guardian", g.name)
		return g

	@frappe.whitelist()
	def pay_registration(self, mode_of_payment, amount=None, reference=None):
		"""The registration fee is received from the guardian and stays as an advance: the first fees invoice uses it."""
		if self.status in ("Rejected", "Withdrawn"):
			frappe.throw(_("The application is {0}").format(_(self.status)))
		if self.registration_paid:
			frappe.throw(_("The registration fee is already paid"))
		amount = flt(amount) or flt(self.registration_fee)
		if amount <= 0:
			frappe.throw(_("Enter the registration fee"))
		g = self._guardian()
		pe = accounting.payment(g.customer, amount, accounting.money_account(mode_of_payment),
			remarks=_("Registration fee - {0}").format(self.applicant_name), reference=reference or self.name)
		self.db_set({"registration_entry": pe, "registration_paid": 1, "registration_fee": amount})
		return pe

	@frappe.whitelist()
	def enroll(self, section=None):
		if self.status != "Accepted":
			frappe.throw(_("Accept the application first"))
		g = self._guardian()
		stu = frappe.get_doc({"doctype": "Student", "student_name": self.applicant_name, "birth_date": self.birth_date, "gender": self.gender,
			"national_id": self.national_id, "previous_school": self.previous_school, "grade_level": self.grade_level,
			"academic_year": self.academic_year, "section": section, "admission_date": nowdate(),
			"guardians": [{"guardian": g.name, "relation": "Father", "is_payer": 1}]})
		stu.insert(ignore_permissions=True)
		self.db_set({"student": stu.name, "status": "Enrolled"})
		return stu.name
