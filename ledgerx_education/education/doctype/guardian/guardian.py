import frappe
from frappe import _
from frappe.model.document import Document

from ledgerx_education.engine import accounting


class Guardian(Document):
	def validate(self):
		if self.is_new() and self.national_id and frappe.db.exists("Guardian", {"national_id": self.national_id}):
			frappe.throw(_("A guardian with this national ID already exists"))

	def after_insert(self):
		try:
			accounting.ensure_customer(self)
		except Exception:
			frappe.log_error(title="Education: could not create the customer of a guardian")
