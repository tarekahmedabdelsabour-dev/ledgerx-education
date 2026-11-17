import frappe
from frappe import _
from frappe.model.document import Document

from ledgerx_education.education.doctype.class_section.class_section import recount


class Student(Document):
	def validate(self):
		self._guardians()
		self._sibling_order()
		if self.section:
			sec = frappe.db.get_value("Class Section", self.section, ["grade_level", "capacity", "strength"], as_dict=True)
			if sec.grade_level != self.grade_level:
				frappe.throw(_("The section {0} belongs to another grade").format(self.section))
			before = self.get_doc_before_save()
			if self.status == "Active" and (not before or before.section != self.section) and sec.capacity and sec.strength >= sec.capacity:
				frappe.msgprint(_("The section is full ({0} of {1})").format(sec.strength, sec.capacity), indicator="orange")

	def _guardians(self):
		if not self.guardians:
			frappe.throw(_("Add at least one guardian"))
		payers = [g for g in self.guardians if g.is_payer]
		if not payers and len(self.guardians) == 1:
			payers = self.guardians
			payers[0].is_payer = 1
		if len(payers) != 1:
			frappe.throw(_("Mark exactly one guardian as the one who pays the fees"))
		self.payer = payers[0].guardian
		g = frappe.get_doc("Guardian", self.payer)
		from ledgerx_education.engine import accounting

		self.customer = accounting.ensure_customer(g)

	def _sibling_order(self):
		"""Eldest first: by date of birth, then by when the child joined."""
		far = "9999-12-31"
		kids = frappe.get_all("Student", filters={"payer": self.payer, "status": "Active", "name": ["!=", self.name or ""]},
			fields=["name", "birth_date", "creation"])
		mine = (str(self.birth_date or far), str(self.creation or "9999"))
		self.sibling_order = 1 + sum(1 for k in kids if (str(k.birth_date or far), str(k.creation)) < mine)

	def on_update(self):
		before = self.get_doc_before_save()
		for sec in {self.section, before.section if before else None}:
			recount(sec)

	def on_trash(self):
		recount(self.section)
