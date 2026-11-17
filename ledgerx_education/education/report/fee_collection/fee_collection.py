import frappe
from frappe import _


def execute(filters=None):
	"""Invoiced, collected and still due, per grade or year."""
	filters = filters or {}
	args, cond = [], ""
	if filters.get("academic_year"):
		cond += " and f.academic_year = %s"
		args.append(filters["academic_year"])
	if filters.get("institution"):
		cond += " and st.institution = %s"
		args.append(filters["institution"])
	rows = frappe.db.sql(
		f"""select st.grade_level, count(distinct f.student) as students, sum(i.grand_total) as invoiced,
		sum(i.grand_total - i.outstanding_amount) as collected, sum(i.outstanding_amount) as due
		from `tabStudent Fee` f join `tabSales Invoice` i on i.name = f.sales_invoice and i.docstatus = 1
		join `tabStudent` st on st.name = f.student where f.status = 'Invoiced' {cond}
		group by st.grade_level order by st.grade_level""", args, as_dict=True)
	for r in rows:
		r["rate"] = round((r.collected or 0) * 100 / r.invoiced, 1) if r.invoiced else 0
	cols = [
		{"label": _("Grade or Year"), "fieldname": "grade_level", "fieldtype": "Link", "options": "Grade Level", "width": 180},
		{"label": _("Students"), "fieldname": "students", "fieldtype": "Int", "width": 80},
		{"label": _("Invoiced"), "fieldname": "invoiced", "fieldtype": "Currency", "width": 130},
		{"label": _("Collected"), "fieldname": "collected", "fieldtype": "Currency", "width": 130},
		{"label": _("Still Due"), "fieldname": "due", "fieldtype": "Currency", "width": 130},
		{"label": _("Collected (%)"), "fieldname": "rate", "fieldtype": "Percent", "width": 110},
	]
	chart = {"data": {"labels": [r.grade_level for r in rows], "datasets": [{"name": _("Collected"), "values": [r.collected or 0 for r in rows]},
		{"name": _("Still Due"), "values": [r.due or 0 for r in rows]}]}, "type": "bar", "stacked": 1}
	return cols, rows, None, chart
