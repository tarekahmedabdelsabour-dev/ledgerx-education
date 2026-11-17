app_name = "ledgerx_education"
app_title = "Education"
app_publisher = "LedgerX"
app_description = "Education management from nursery to university: admissions, students, academic structure, fees and installments, attendance, grades"
app_email = "hello@ledgerx.local"
app_license = "mit"

required_apps = ["erpnext", "hrms"]

add_to_apps_screen = [
	{
		"name": "ledgerx_education",
		"logo": "/assets/ledgerx_education/images/education.svg",
		"title": "Education",
		"route": "/desk/education",
		"has_permission": "ledgerx_education.install.check_app_permission",
	}
]

override_doctype_dashboards = {
	"Customer": "ledgerx_education.overrides.customer",
	"Employee": "ledgerx_education.overrides.employee",
	"Sales Invoice": "ledgerx_education.overrides.sales_invoice",
	"Payment Entry": "ledgerx_education.overrides.payment_entry",
	"Vehicle": "ledgerx_education.overrides.vehicle",
}

scheduler_events = {
	"cron": {
		"0 7 * * *": ["ledgerx_education.tasks.absence_alerts"],
	},
}

after_install = "ledgerx_education.install.after_install"
after_migrate = "ledgerx_education.install.after_migrate"
