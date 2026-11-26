"""Install and migrate steps. Each is idempotent and a failing step never aborts a migrate."""
import os

import frappe

MODULE = "Education"
ROLES = ["Education Manager", "Education Registrar", "Education Teacher", "Education Accountant"]
CATEGORIES = ["Tuition", "Books", "Uniform", "Bus", "Activities"]
SCALE = [(0, "Fail", 0), (50, "Pass", 1), (65, "Good", 2), (75, "Very Good", 3), (85, "Excellent", 4)]


def check_app_permission():
	if frappe.session.user == "Administrator":
		return True
	return bool(set(frappe.get_roles()) & set(ROLES + ["System Manager"]))


def after_install():
	_all()


def after_migrate():
	_all()


def _all():
	for fn in (ensure_module, ensure_roles, ensure_settings, ensure_scale, ensure_categories, refresh_workspace):
		try:
			fn()
			frappe.db.commit()
		except Exception:
			frappe.db.rollback()
			frappe.log_error(title=f"ledgerx_education install step failed: {fn.__name__}")
	frappe.clear_cache()


def ensure_module():
	if not frappe.db.exists("Module Def", MODULE):
		frappe.get_doc({"doctype": "Module Def", "module_name": MODULE, "app_name": "ledgerx_education"}).insert(ignore_permissions=True)


def ensure_roles():
	for role in ROLES:
		if not frappe.db.exists("Role", role):
			frappe.get_doc({"doctype": "Role", "role_name": role, "desk_access": 1}).insert(ignore_permissions=True)


def ensure_scale():
	if frappe.db.exists("Grading Scale", "Default"):
		return
	frappe.get_doc({"doctype": "Grading Scale", "scale_name": "Default",
		"ranges": [{"from_percent": a, "grade": b, "points": c} for a, b, c in SCALE]}).insert(ignore_permissions=True)


def ensure_settings():
	s = frappe.get_doc("Education Settings")
	changed = False
	if not s.company:
		s.company = frappe.db.get_single_value("Global Defaults", "default_company") or frappe.db.get_value("Company", {}, "name")
		changed = bool(s.company)
	if not s.grading_scale and frappe.db.exists("Grading Scale", "Default"):
		s.grading_scale, changed = "Default", True
	if changed and s.company:
		s.flags.ignore_mandatory = True  # the accounts are chosen later, in the settings form
		s.save(ignore_permissions=True)


def ensure_categories():
	for c in CATEGORIES:
		if not frappe.db.exists("Fee Category", c):
			frappe.get_doc({"doctype": "Fee Category", "category_name": c}).insert(ignore_permissions=True)


def refresh_workspace():
	"""Migrate only re-reads a workspace file that is newer than the saved one: force it."""
	base = os.path.join(frappe.get_app_path("ledgerx_education"), "education")
	for dt in ("number_card", "dashboard_chart"):
		folder = os.path.join(base, dt)
		for name in sorted(os.listdir(folder)) if os.path.isdir(folder) else []:
			if os.path.isdir(os.path.join(folder, name)):
				frappe.reload_doc("education", dt, name, force=True)
	frappe.reload_doc("education", "workspace", "education", force=True)
