import frappe
from frappe import _
from frappe.model.document import Document


class FeeStructure(Document):
	def validate(self):
		if not self.items:
			frappe.throw(_("Add at least one fee"))
		if int(self.installments or 1) < 1:
			frappe.throw(_("There is at least one installment"))
		if self.active and frappe.db.exists("Fee Structure", {"academic_year": self.academic_year, "grade_level": self.grade_level, "active": 1,
				"name": ["!=", self.name or ""]}):
			frappe.throw(_("There is already an active fee structure for this grade and year"))
