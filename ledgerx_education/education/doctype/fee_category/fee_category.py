from frappe.model.document import Document

from ledgerx_education.engine import accounting


class FeeCategory(Document):
	def after_insert(self):
		accounting.item_for(self.name)
