import frappe
from frappe import _
from frappe.model.document import Document


def recount(section):
	if section and frappe.db.exists("Class Section", section):
		n = frappe.db.count("Student", {"section": section, "status": "Active"})
		frappe.db.set_value("Class Section", section, "strength", n, update_modified=False)


class ClassSection(Document):
	def validate(self):
		if self.capacity and self.capacity < 0:
			frappe.throw(_("Capacity cannot be negative"))
		self.strength = frappe.db.count("Student", {"section": self.name, "status": "Active"}) if not self.is_new() else 0
