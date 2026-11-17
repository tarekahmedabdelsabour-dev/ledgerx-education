"""Writes the workspace, sidebar and dock JSON of ledgerx_education. Run from the repo root."""
import json
import os
import uuid

BASE = os.path.join(os.path.dirname(__file__), "..", "ledgerx_education")
TS = "2026-11-17 09:00:00.000000"  # raise this whenever the workspace changes: migrate only re-reads a file that is newer than the saved one
CARDS = [  # (label, doctype, filters, function, fn_field)
	("Active Students", "Student", [["Student", "status", "=", "Active"]], "Count", None),
	("New Applications", "Admission Application", [["Admission Application", "status", "=", "New"]], "Count", None),
	("Interviews Scheduled", "Admission Application", [["Admission Application", "status", "=", "Interview Scheduled"]], "Count", None),
	("Accepted, Not Enrolled", "Admission Application", [["Admission Application", "status", "=", "Accepted"]], "Count", None),
	("Fees to Invoice", "Student Fee", [["Student Fee", "status", "=", "Draft"]], "Count", None),
	("Invoiced Fees", "Student Fee", [["Student Fee", "status", "=", "Invoiced"]], "Count", None),
	("Registrations to Confirm", "Course Registration", [["Course Registration", "status", "=", "Draft"]], "Count", None),
	("Open Courses", "Course Offering", [["Course Offering", "status", "=", "Open"]], "Count", None),
]
CHARTS = [  # (name, doctype, type, kind, extra)
	("Students by Grade", "Student", "Bar", "group", {"by": "grade_level"}),
	("Students by Stage", "Student", "Donut", "group", {"by": "stage"}),
	("Applications by Status", "Admission Application", "Donut", "group", {"by": "status"}),
	("Applications per Month", "Admission Application", "Bar", "series", {"based_on": "application_date", "filters": [["Admission Application", "status", "not in", ["Rejected", "Withdrawn"]]]}),
]
GROUPS = [  # (title, icon, collapsed, [(label, kind, target, icon)])
	("Daily Work", None, 0, [
		("Student", "DocType", "Student", "graduation-cap"), ("Admission Application", "DocType", "Admission Application", "file-pen"),
		("Student Fee", "DocType", "Student Fee", "receipt"), ("Class Attendance", "DocType", "Class Attendance", "check-square"),
		("Mark Sheet", "DocType", "Mark Sheet", "pencil"), ("Guardian", "DocType", "Guardian", "user-round")]),
	("Academics", "school", 0, [
		("Academic Year", "DocType", "Academic Year", "calendar"), ("Education Stage", "DocType", "Education Stage", "layers"),
		("Grade Level", "DocType", "Grade Level", "signal"), ("Class Section", "DocType", "Class Section", "users"),
		("Subject", "DocType", "Subject", "book-open"), ("Course Offering", "DocType", "Course Offering", "clock"),
		("Course Registration", "DocType", "Course Registration", "list-checks"), ("Faculty", "DocType", "Faculty", "building"),
		("Academic Department", "DocType", "Academic Department", "network"), ("Grading Scale", "DocType", "Grading Scale", "list-ordered")]),
	("Fees", "wallet", 0, [
		("Fee Category", "DocType", "Fee Category", "tag"), ("Fee Structure", "DocType", "Fee Structure", "list"),
		("Scholarship", "DocType", "Scholarship", "award")]),
	("Reports", "bar-chart-3", 0, [
		("Fees Due", "Report", "Fees Due", "alarm-clock"), ("Fee Collection", "Report", "Fee Collection", "trending-up"),
		("Class Strength", "Report", "Class Strength", "users"), ("Attendance Summary", "Report", "Attendance Summary", "check-square"),
		("Student Report Card", "Report", "Student Report Card", "file-text")]),
	("Setup", "settings", 1, [
		("Education Institution", "DocType", "Education Institution", "landmark"), ("Education Settings", "DocType", "Education Settings", "settings")]),
	("Related", "link-2", 1, [
		("Customer", "DocType", "Customer", "users"), ("Sales Invoice", "DocType", "Sales Invoice", "receipt"),
		("Payment Entry", "DocType", "Payment Entry", "wallet"), ("Employee", "DocType", "Employee", "user-round"),
		("Vehicle", "DocType", "Vehicle", "bus")]),
]
TOP = ["Student", "Admission Application", "Student Fee", "Class Attendance"]
REPORTS = {"Fees Due", "Fee Collection", "Class Strength", "Attendance Summary", "Student Report Card"}


def write(path, data):
	os.makedirs(os.path.dirname(path), exist_ok=True)
	with open(path, "w", encoding="utf-8") as fh:
		json.dump(data, fh, indent=1, ensure_ascii=False)
		fh.write("\n")


def slug(n):
	return n.lower().replace(" ", "_").replace("-", "_")


def write_cards():
	for label, dt, flt, fn, _f in CARDS:
		write(os.path.join(BASE, "education", "number_card", slug(label), slug(label) + ".json"), {
			"creation": TS, "docstatus": 0, "doctype": "Number Card", "document_type": dt, "filters_json": json.dumps(flt), "function": fn,
			"idx": 0, "is_public": 1, "is_standard": 1, "label": label, "modified": TS, "modified_by": "Administrator", "module": "Education",
			"name": label, "owner": "Administrator", "show_percentage_stats": 0, "stats_time_interval": "Daily", "type": "Document Type"})
	for name, dt, typ, kind, x in CHARTS:
		d = {"chart_name": name, "creation": TS, "docstatus": 0, "doctype": "Dashboard Chart", "document_type": dt, "dynamic_filters_json": "",
			"idx": 0, "is_public": 1, "is_standard": 1, "modified": TS, "modified_by": "Administrator", "module": "Education", "name": name,
			"number_of_groups": 0, "owner": "Administrator", "type": typ, "use_report_chart": 0, "y_axis": []}
		if kind == "group":
			d.update({"chart_type": "Group By", "group_by_based_on": x["by"], "group_by_type": "Count", "filters_json": "[]", "timeseries": 0})
		else:
			d.update({"chart_type": "Count", "based_on": x["based_on"], "filters_json": json.dumps(x["filters"]), "time_interval": "Monthly",
				"timeseries": 1, "timespan": "Last Year"})
		write(os.path.join(BASE, "education", "dashboard_chart", slug(name), slug(name) + ".json"), d)


def main():
	write_cards()
	rid = lambda: uuid.uuid4().hex[:10]
	content = [{"id": rid(), "type": "header", "data": {"text": '<span class="h4"><b>Education</b></span>', "col": 12}}]
	for label, *_r in CARDS:
		content.append({"id": rid(), "type": "number_card", "data": {"number_card_name": label, "col": 3}})
	for name, *_r in CHARTS:
		content.append({"id": rid(), "type": "chart", "data": {"chart_name": name, "col": 6}})
	shortcuts, links = [], []
	for label in TOP:
		content.insert(1 + len(shortcuts), {"id": rid(), "type": "shortcut", "data": {"shortcut_name": label, "col": 3}})
		kind = "Report" if label in REPORTS else "DocType"
		sc = {"label": label, "link_to": label, "type": kind}
		if kind == "DocType":
			sc["doc_view"] = "List"
		else:
			sc["is_query_report"] = 1
		shortcuts.append(sc)
	for title, _i, _c, items in GROUPS[1:]:
		content.append({"id": rid(), "type": "card", "data": {"card_name": title, "col": 4}})
		links.append({"type": "Card Break", "label": title, "hidden": 0, "is_query_report": 0, "link_count": len(items), "onboard": 0})
		for label, kind, target, _icon in items:
			links.append({"type": "Link", "label": label, "link_type": kind, "link_to": target, "hidden": 0, "is_query_report": 1 if kind == "Report" else 0,
				"onboard": 0, "dependencies": "", "only_for": ""})
	write(os.path.join(BASE, "education", "workspace", "education", "education.json"), {
		"charts": [{"chart_name": c[0], "label": c[0]} for c in CHARTS], "content": json.dumps(content), "creation": TS, "custom_blocks": [], "docstatus": 0, "doctype": "Workspace",
		"for_user": "", "hide_custom": 1, "icon": "graduation-cap", "idx": 1, "is_hidden": 0, "label": "Education", "links": links, "title": "Education", "modified": TS,
		"modified_by": "Administrator", "module": "Education", "name": "Education", "number_cards": [{"label": c[0], "number_card_name": c[0]} for c in CARDS], "owner": "Administrator",
		"parent_page": "", "public": 1, "quick_lists": [], "roles": [], "sequence_id": 23.0, "shortcuts": shortcuts})
	row = lambda i, label, kind, target, icon, child: {"child": child, "collapsible": 1, "doctype": "Sidebar Item", "icon": icon, "idx": i, "indent": 0,
		"keep_closed": 0, "label": label, "link_to": target, "link_type": kind, "parentfield": "items", "parenttype": "Sidebar", "show_arrow": 0, "type": "Link"}
	items = [row(1, "Home", "Workspace", "Education", "house", 0)]
	for title, icon, closed, entries in GROUPS:
		if icon:
			items.append({"child": 0, "collapsible": 1, "doctype": "Sidebar Item", "icon": icon, "idx": len(items) + 1, "indent": 1, "keep_closed": closed,
				"label": title, "link_type": "DocType", "parentfield": "items", "parenttype": "Sidebar", "show_arrow": 0, "type": "Section Break"})
		for label, kind, target, ic in entries:
			items.append(row(len(items) + 1, label, kind, target, ic, 1 if icon else 0))
	write(os.path.join(BASE, "sidebar", "education", "education.json"), {"app": "ledgerx_education", "doctype": "Sidebar", "header_icon": "graduation-cap",
		"items": items, "module": "Education", "name": "Education", "standard": 1, "title": "Education"})
	write(os.path.join(BASE, "dock", "education", "education.json"), {"app": "ledgerx_education", "creation": TS, "docstatus": 0, "doctype": "Dock", "idx": 0,
		"items": [{"added": 0, "hidden": 0, "icon": "graduation-cap", "link_to": "Education", "link_type": "Sidebar", "title": "Education"}],
		"modified": TS, "modified_by": "Administrator", "name": "education", "owner": "Administrator", "standard": 1})


main()
