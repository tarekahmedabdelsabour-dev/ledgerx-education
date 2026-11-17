import frappe
from frappe import _
from frappe.utils import add_days, getdate, nowdate


def execute(filters=None):
	"""Every unpaid installment of a fees invoice, oldest first. Late ones show how many days."""
	filters = filters or {}
	until = filters.get("until") or add_days(nowdate(), 30)
	args, cond = [until], ""
	if filters.get("grade_level"):
		cond += " and st.grade_level = %s"
		args.append(filters["grade_level"])
	if filters.get("institution"):
		cond += " and st.institution = %s"
		args.append(filters["institution"])
	rows = frappe.db.sql(
		f"""select p.due_date, (p.payment_amount - p.paid_amount) as due, f.student, f.student_name, st.grade_level, st.section, f.customer,
		g.phone, f.name as fee, i.name as invoice
		from `tabPayment Schedule` p join `tabSales Invoice` i on i.name = p.parent
		join `tabStudent Fee` f on f.sales_invoice = i.name join `tabStudent` st on st.name = f.student
		left join `tabGuardian` g on g.name = st.payer
		where p.parenttype = 'Sales Invoice' and i.docstatus = 1 and p.payment_amount - p.paid_amount > 0.005 and p.due_date <= %s {cond}
		order by p.due_date""", args, as_dict=True)
	today = getdate(nowdate())
	for r in rows:
		r["late_days"] = max((today - getdate(r.due_date)).days, 0)
	cols = [
		{"label": _("Due Date"), "fieldname": "due_date", "fieldtype": "Date", "width": 100},
		{"label": _("Days Late"), "fieldname": "late_days", "fieldtype": "Int", "width": 80},
		{"label": _("Amount Due"), "fieldname": "due", "fieldtype": "Currency", "width": 120},
		{"label": _("Student"), "fieldname": "student_name", "fieldtype": "Data", "width": 170},
		{"label": _("Grade or Year"), "fieldname": "grade_level", "fieldtype": "Link", "options": "Grade Level", "width": 140},
		{"label": _("Section"), "fieldname": "section", "fieldtype": "Link", "options": "Class Section", "width": 120},
		{"label": _("Guardian Phone"), "fieldname": "phone", "fieldtype": "Data", "width": 120},
		{"label": _("Fees"), "fieldname": "fee", "fieldtype": "Link", "options": "Student Fee", "width": 140},
		{"label": _("Invoice"), "fieldname": "invoice", "fieldtype": "Link", "options": "Sales Invoice", "width": 140},
	]
	return cols, rows
