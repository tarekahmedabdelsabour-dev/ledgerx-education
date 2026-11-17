"""Customers, invoices and payments of the education module, all on ERPNext's own documents."""
import frappe
from frappe import _
from frappe.utils import flt, nowdate

from ledgerx_education.engine import logic


def settings():
	return frappe.get_cached_doc("Education Settings")


def need(s, field, label):
	if not s.get(field):
		frappe.throw(_("Set {0} in Education Settings first").format(_(label)))
	return s.get(field)


def cost_center_of(institution):
	return frappe.db.get_value("Education Institution", institution, "cost_center") if institution else None


def ensure_customer(guardian):
	"""Every guardian has a customer: fees are invoiced to it and payments are received from it."""
	if guardian.customer and frappe.db.exists("Customer", guardian.customer):
		return guardian.customer
	name = guardian.guardian_name
	if frappe.db.exists("Customer", name):
		name = f"{guardian.guardian_name} ({guardian.phone})"
	group = "Individual" if frappe.db.exists("Customer Group", "Individual") else frappe.db.get_value("Customer Group", {"is_group": 0}, "name")
	territory = frappe.db.get_value("Territory", {"is_group": 0}, "name")
	cust = frappe.get_doc({"doctype": "Customer", "customer_name": name, "customer_type": "Individual", "customer_group": group, "territory": territory,
		"mobile_no": guardian.phone, "email_id": guardian.email})
	cust.insert(ignore_permissions=True)
	guardian.db_set("customer", cust.name)
	return cust.name


def item_for(category):
	"""The invoice item of a fee category (created on first use)."""
	item = frappe.db.get_value("Fee Category", category, "item")
	if item and frappe.db.exists("Item", item):
		return item
	code = f"Fee - {category}"
	if not frappe.db.exists("Item", code):
		group = "Services" if frappe.db.exists("Item Group", "Services") else "All Item Groups"
		uom = "Nos" if frappe.db.exists("UOM", "Nos") else frappe.db.get_value("UOM", {}, "name")
		frappe.get_doc({"doctype": "Item", "item_code": code, "item_name": code, "item_group": group, "stock_uom": uom, "is_stock_item": 0,
			"is_sales_item": 1, "is_purchase_item": 0, "include_item_in_manufacturing": 0}).insert(ignore_permissions=True)
	frappe.db.set_value("Fee Category", category, "item", code)
	return code


def money_account(mode_of_payment):
	from erpnext.accounts.doctype.sales_invoice.sales_invoice import get_bank_cash_account

	acc = (get_bank_cash_account(mode_of_payment, settings().company) or {}).get("account")
	if not acc:
		frappe.throw(_("Mode of Payment {0} has no account for the company").format(mode_of_payment))
	return acc


def payment(customer, amount, account, invoice=None, remarks="", refund=False, reference=None):
	"""Receive money from a guardian (or pay it back). With an invoice the amount is allocated to it."""
	from erpnext.accounts.party import get_party_account

	company = settings().company
	receivable = get_party_account("Customer", customer, company)
	amount = flt(amount)
	pe = frappe.new_doc("Payment Entry")
	pe.update({"payment_type": "Pay" if refund else "Receive", "company": company, "posting_date": nowdate(), "party_type": "Customer",
		"party": customer, "remarks": remarks, "reference_no": reference or remarks[:40] or "-", "reference_date": nowdate()})
	if refund:
		pe.update({"paid_from": account, "paid_to": receivable, "paid_amount": amount, "received_amount": amount})
	else:
		pe.update({"paid_from": receivable, "paid_to": account, "paid_amount": amount, "received_amount": logic.r2(amount)})
	if invoice:
		pe.append("references", {"reference_doctype": "Sales Invoice", "reference_name": invoice, "allocated_amount": amount})
	pe.insert(ignore_permissions=True)
	pe.submit()
	return pe.name
