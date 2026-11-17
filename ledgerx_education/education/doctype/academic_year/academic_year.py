import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class AcademicYear(Document):
	def validate(self):
		if getdate(self.end_date) <= getdate(self.start_date):
			frappe.throw(_("The year must end after it starts"))
		for t in self.terms:
			if getdate(t.end_date) < getdate(t.start_date):
				frappe.throw(_("Row {0}: the term ends before it starts").format(t.idx))
			if not getdate(self.start_date) <= getdate(t.start_date) <= getdate(t.end_date) <= getdate(self.end_date):
				frappe.throw(_("Row {0}: the term is outside the academic year").format(t.idx))

	def on_update(self):
		if self.is_current:
			frappe.db.sql("update `tabAcademic Year` set is_current = 0 where name != %s", self.name)
