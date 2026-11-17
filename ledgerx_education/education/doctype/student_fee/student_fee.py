import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

from ledgerx_education.engine import accounting, logic


class StudentFee(Document):
	def validate(self):
		if self.status != "Draft" and not self.is_new():
			return
		s = accounting.settings()
		stu = frappe.db.get_value("Student", self.student, ["grade_level", "customer", "sibling_order", "scholarship", "status"], as_dict=True)
		if stu.status != "Active":
			frappe.throw(_("The student is {0}").format(_(stu.status)))
		self.customer = stu.customer
		struct = None
		if not self.fee_structure:
			self.fee_structure = frappe.db.get_value("Fee Structure", {"academic_year": self.academic_year, "grade_level": stu.grade_level, "active": 1}, "name")
		if self.fee_structure:
			struct = frappe.get_doc("Fee Structure", self.fee_structure)
		if self.is_new():
			if struct and not self.items:
				for it in struct.items:
					self.append("items", {"fee_category": it.fee_category, "amount": it.amount})
				self.installments, self.interval_months = struct.installments, struct.interval_months
			elif not self.installments:
				self.installments, self.interval_months = s.default_installments or 1, s.interval_months or 1
			if not flt(self.sibling_discount_pct):
				self.sibling_discount_pct = logic.sibling_discount_pct(stu.sibling_order, s.sibling_pct_2, s.sibling_pct_3, s.sibling_pct_4)
			if stu.scholarship and not flt(self.scholarship_pct) and not flt(self.scholarship_amount):
				sc = frappe.db.get_value("Scholarship", stu.scholarship, ["discount_pct", "discount_amount", "active"], as_dict=True)
				if sc and sc.active:
					self.scholarship_pct, self.scholarship_amount = sc.discount_pct, sc.discount_amount
		if not self.items:
			frappe.throw(_("Add the fees: choose a fee structure or add lines"))
		t = logic.fee_totals([i.amount for i in self.items], self.sibling_discount_pct, self.scholarship_pct, self.scholarship_amount, s.vat_rate)
		self.gross, self.sibling_discount, self.scholarship, self.net, self.vat, self.total = t["gross"], t["sibling_discount"], t["scholarship"], t["net"], t["vat"], t["total"]
		if self.is_new() and struct and flt(struct.down_payment_pct) and not flt(self.down_payment):
			self.down_payment = logic.r2(self.total * flt(struct.down_payment_pct) / 100)
		if flt(self.down_payment) > self.total + 0.005:
			frappe.throw(_("The down payment is more than the total"))

	def _need(self, *statuses):
		if self.status not in statuses:
			frappe.throw(_("The fee is {0}").format(_(self.status)))

	@frappe.whitelist()
	def confirm(self):
		"""Invoice the guardian. Money already received from this customer (registration fee, advances) is applied."""
		self._need("Draft")
		s = accounting.settings()
		if self.total <= 0:
			frappe.throw(_("There is nothing to invoice"))
		institution = frappe.db.get_value("Student", self.student, "institution")
		cc = accounting.cost_center_of(institution)
		inv = frappe.new_doc("Sales Invoice")
		inv.update({"customer": self.customer, "company": s.company, "posting_date": self.posting_date, "due_date": self.first_due_date, "cost_center": cc,
			"update_stock": 0, "ignore_pricing_rule": 1, "allocate_advances_automatically": 1,
			"selling_price_list": frappe.db.get_value("Price List", {"selling": 1, "enabled": 1}, "name"),
			"remarks": _("Fees of {0} - {1}").format(self.student_name, self.academic_year)})
		for it in self.items:
			cat = frappe.db.get_value("Fee Category", it.fee_category, ["income_account"], as_dict=True)
			inv.append("items", {"item_code": accounting.item_for(it.fee_category), "qty": 1, "rate": flt(it.amount), "cost_center": cc,
				"income_account": cat.income_account or accounting.need(s, "default_income_account", "Default Fees Income Account"),
				"description": f"{it.fee_category} - {self.student_name}" + (f" ({it.description})" if it.description else "")})
		discount = logic.r2(self.sibling_discount + self.scholarship)
		if discount:
			inv.apply_discount_on = "Net Total"
			inv.discount_amount = discount
		if self.vat:
			inv.append("taxes", {"charge_type": "Actual", "account_head": accounting.need(s, "vat_account", "VAT Account"), "description": _("VAT"),
				"tax_amount": self.vat, "cost_center": cc})
		for due, amount in logic.installment_schedule(self.total, self.installments, self.first_due_date, self.interval_months, self.down_payment, self.posting_date):
			inv.append("payment_schedule", {"due_date": due, "payment_amount": amount, "invoice_portion": 0})
		inv.insert(ignore_permissions=True)
		inv.set_advances()
		if inv.get("advances"):
			inv.save(ignore_permissions=True)
		inv.submit()
		self.db_set({"status": "Invoiced", "sales_invoice": inv.name})
		self.reload()
		return inv.name

	@frappe.whitelist()
	def receive_payment(self, mode_of_payment, amount, reference=None):
		"""A down payment or an installment: any amount up to what is still due."""
		self._need("Invoiced")
		out = flt(frappe.db.get_value("Sales Invoice", self.sales_invoice, "outstanding_amount"))
		amount = flt(amount)
		if amount <= 0 or amount > out + 0.005:
			frappe.throw(_("The amount must be above zero and not more than the {0} still due").format(out))
		return accounting.payment(self.customer, amount, accounting.money_account(mode_of_payment), self.sales_invoice,
			_("Fees of {0} - {1}").format(self.student_name, self.name), reference=reference)

	@frappe.whitelist()
	def add_credit_hours(self, registration):
		"""University: add a line for the credit hours the student registered."""
		self._need("Draft")
		reg = frappe.db.get_value("Course Registration", registration, ["student", "status", "total_credit_hours"], as_dict=True)
		if not reg or reg.student != self.student or reg.status != "Confirmed":
			frappe.throw(_("Choose a confirmed registration of this student"))
		fee = flt(frappe.db.get_value("Fee Structure", self.fee_structure, "credit_hour_fee")) if self.fee_structure else 0
		if not fee:
			frappe.throw(_("The fee structure has no fee per credit hour"))
		if not frappe.db.exists("Fee Category", "Credit Hours"):
			frappe.get_doc({"doctype": "Fee Category", "category_name": "Credit Hours"}).insert(ignore_permissions=True)
		self.append("items", {"fee_category": "Credit Hours", "description": _("{0} credit hours").format(reg.total_credit_hours),
			"amount": logic.r2(fee * flt(reg.total_credit_hours))})
		self.save()
		return self.total

	@frappe.whitelist()
	def cancel_draft(self):
		self._need("Draft")
		self.db_set("status", "Cancelled")
