"""Shows the education documents in the "Connections" panel of the records they belong to."""
from frappe import _


def _group(data, label, items, fields=None):
	data = data or {}
	data.setdefault("transactions", [])
	data["transactions"].append({"label": _(label), "items": items})
	if fields:
		data.setdefault("non_standard_fieldnames", {}).update(fields)
	return data


def customer(data=None):
	return _group(data, "Education", ["Guardian", "Student", "Student Fee"])


def employee(data=None):
	return _group(data, "Education", ["Class Section", "Course Offering", "Class Attendance"],
		{"Class Section": "homeroom_teacher", "Course Offering": "teacher", "Class Attendance": "taken_by"})


def sales_invoice(data=None):
	return _group(data, "Education", ["Student Fee"], {"Student Fee": "sales_invoice"})


def payment_entry(data=None):
	return _group(data, "Education", ["Admission Application"], {"Admission Application": "registration_entry"})


def vehicle(data=None):
	return _group(data, "Education", ["Student"], {"Student": "transport_vehicle"})
