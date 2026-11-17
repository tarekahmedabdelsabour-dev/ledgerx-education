"""Builds every DocType JSON of ledgerx_education from the compact table below.
Run from the repo root:  python3 tools/gen_doctypes.py   (rewrites ledgerx_education/education/doctype/*)"""
import json
import os
import re

ROOT = os.path.join(os.path.dirname(__file__), "..", "ledgerx_education", "education", "doctype")
TS = "2026-11-17 08:00:00.000000"
MODULE = "Education"

MGR, REG, TCH, ACC = "Education Manager", "Education Registrar", "Education Teacher", "Education Accountant"


def f(name, ftype, label=None, **kw):
	d = {"fieldname": name, "fieldtype": ftype}
	if ftype not in ("Section Break", "Column Break", "Tab Break"):
		d["label"] = label or name.replace("_", " ").title()
	elif label:
		d["label"] = label
	d.update(kw)
	return d


def sec(name, label=None, **kw):
	return f(name, "Section Break", label, **kw)


def col(name):
	return f(name, "Column Break")


def perms(*rows):
	out = []
	for role, mode in rows:
		p = {"role": role, "read": 1, "report": 1, "print": 1, "export": 1}
		if mode in ("rw", "rwc", "all"):
			p["write"] = 1
		if mode in ("rwc", "all"):
			p["create"] = 1
		if mode == "all":
			p["delete"] = 1
		out.append(p)
	out.append({"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "print": 1, "export": 1})
	return out


DT = {}


def doctype(name, fields, **kw):
	DT[name] = {"name": name, "fields": fields, **kw}


CUR = {"options": "currency"}

ACCT = lambda n, l, **k: f(n, "Link", l, options="Account", **k)


STU = lambda: perms((MGR, "all"), (REG, "all"), (TCH, "r"), (ACC, "r"))
STRUCT_ = perms((MGR, "all"), (REG, "r"), (TCH, "r"), (ACC, "r"))
MONEY = lambda: perms((MGR, "all"), (ACC, "all"), (REG, "r"))
CLASS = lambda: perms((MGR, "all"), (TCH, "all"), (REG, "r"))

doctype("Education Settings", [
	f("company", "Link", "Company", options="Company", reqd=1),
	f("default_income_account", "Link", "Default Fees Income Account", options="Account", description="Used by every fee category that has no income account of its own."),
	f("vat_account", "Link", "VAT Account", options="Account"),
	f("vat_rate", "Percent", "VAT on Fees (%)", default=0, description="Most education fees are exempt: leave 0."),
	col("cb1"),
	f("default_installments", "Int", "Default Number of Installments", default=1),
	f("interval_months", "Int", "Months Between Installments", default=1),
	sec("sb_sib", "Sibling Discount"),
	f("sibling_pct_2", "Percent", "Second Child (%)", default=0),
	f("sibling_pct_3", "Percent", "Third Child (%)", default=0),
	col("cb2"),
	f("sibling_pct_4", "Percent", "Fourth Child and After (%)", default=0),
	sec("sb_acad", "Academic"),
	f("grading_scale", "Link", "Default Grading Scale", options="Grading Scale"),
	f("pass_percent", "Percent", "Pass Mark (%)", default=50),
	col("cb3"),
	f("absence_alert", "Int", "Warn the Class Teacher After This Many Absences", default=5),
], issingle=1, icon="fa fa-cog", perms=perms((MGR, "rw"), (ACC, "r")))

# ---------------------------------------------------------------- structure
doctype("Education Institution", [
	f("institution_name", "Data", "Institution", reqd=1, unique=1, in_list_view=1),
	f("institution_type", "Select", "Type", options="Nursery\nSchool\nUniversity\nTraining Center", default="School", in_list_view=1),
	f("company", "Link", "Company", options="Company"),
	f("cost_center", "Link", "Cost Center", options="Cost Center", reqd=1, description="Fees of this institution are posted to it, so each branch or school has its own results."),
	f("active", "Check", "Active", default=1),
	col("cb1"),
	f("head", "Link", "Head", options="Employee"),
	f("city", "Data", "City"),
	f("phone", "Data", "Phone"),
	f("address", "Small Text", "Address"),
], autoname="field:institution_name", title_field="institution_name", icon="fa fa-university", perms=STRUCT_)

doctype("Academic Term", [
	f("term_name", "Data", "Term", reqd=1, in_list_view=1),
	f("start_date", "Date", "From", reqd=1, in_list_view=1),
	f("end_date", "Date", "To", reqd=1, in_list_view=1),
], istable=1)

doctype("Academic Year", [
	f("year_name", "Data", "Academic Year", reqd=1, unique=1, in_list_view=1, description="For example 2026-2027."),
	f("start_date", "Date", "Starts", reqd=1),
	f("end_date", "Date", "Ends", reqd=1),
	f("is_current", "Check", "Current Year", in_list_view=1),
	sec("sb_terms", "Terms or Semesters"),
	f("terms", "Table", "Terms", options="Academic Term"),
], autoname="field:year_name", title_field="year_name", icon="fa fa-calendar", perms=STRUCT_)

doctype("Education Stage", [
	f("stage_name", "Data", "Stage", reqd=1, unique=1, in_list_view=1),
	f("stage_type", "Select", "Kind", options="Nursery\nPrimary\nPreparatory\nSecondary\nUniversity\nOther", reqd=1, in_list_view=1),
	f("institution", "Link", "Institution", options="Education Institution", reqd=1, in_list_view=1),
	f("sort_order", "Int", "Order", default=1),
], autoname="field:stage_name", title_field="stage_name", icon="fa fa-sitemap", perms=STRUCT_)

doctype("Faculty", [
	f("faculty_name", "Data", "Faculty", reqd=1, unique=1, in_list_view=1),
	f("institution", "Link", "Institution", options="Education Institution", reqd=1, in_list_view=1),
	f("dean", "Link", "Dean", options="Employee"),
], autoname="field:faculty_name", title_field="faculty_name", icon="fa fa-building", perms=STRUCT_)

doctype("Academic Department", [
	f("department_name", "Data", "Department", reqd=1, unique=1, in_list_view=1),
	f("faculty", "Link", "Faculty", options="Faculty", reqd=1, in_list_view=1),
	f("head", "Link", "Head of Department", options="Employee"),
], autoname="field:department_name", title_field="department_name", icon="fa fa-sitemap", perms=STRUCT_)

doctype("Grade Level", [
	f("grade_name", "Data", "Grade or Year", reqd=1, in_list_view=1, description="KG1, Grade 4, First Preparatory, Year 2..."),
	f("stage", "Link", "Stage", options="Education Stage", reqd=1, in_list_view=1, in_standard_filter=1),
	f("institution", "Link", "Institution", options="Education Institution", fetch_from="stage.institution", read_only=1),
	f("department", "Link", "Department", options="Academic Department", description="For university years."),
	col("cb1"),
	f("sort_order", "Int", "Order", default=1),
	f("next_grade", "Link", "Promoted To", options="Grade Level", description="Where students go at the end of the year. Empty for the last year."),
], autoname="format:{stage}-{grade_name}", title_field="grade_name", icon="fa fa-level-up", perms=STRUCT_)

doctype("Class Section", [
	f("grade_level", "Link", "Grade or Year", options="Grade Level", reqd=1, in_list_view=1, in_standard_filter=1),
	f("section_name", "Data", "Section", reqd=1, in_list_view=1, description="A, B, 1, Morning..."),
	f("academic_year", "Link", "Academic Year", options="Academic Year", reqd=1, in_list_view=1),
	col("cb1"),
	f("capacity", "Int", "Capacity", default=30),
	f("strength", "Int", "Students", read_only=1, in_list_view=1),
	f("homeroom_teacher", "Link", "Class Teacher", options="Employee"),
	f("room", "Data", "Room"),
], autoname="format:{grade_level}-{section_name}-{academic_year}", title_field="section_name", icon="fa fa-users", perms=STRUCT_)

doctype("Subject", [
	f("subject_name", "Data", "Subject", reqd=1, unique=1, in_list_view=1),
	f("subject_code", "Data", "Code"),
	f("credit_hours", "Float", "Credit Hours", description="University subjects."),
	f("is_elective", "Check", "Elective"),
], autoname="field:subject_name", title_field="subject_name", icon="fa fa-book", perms=STRUCT_)

doctype("Course Schedule Slot", [
	f("day", "Select", "Day", options="Saturday\nSunday\nMonday\nTuesday\nWednesday\nThursday\nFriday", reqd=1, in_list_view=1),
	f("from_time", "Time", "From", reqd=1, in_list_view=1),
	f("to_time", "Time", "To", reqd=1, in_list_view=1),
	f("room", "Data", "Room", in_list_view=1),
], istable=1)

doctype("Course Offering", [
	f("title", "Data", "Title", read_only=1, in_list_view=1),
	f("subject", "Link", "Subject", options="Subject", reqd=1, in_list_view=1),
	f("academic_year", "Link", "Academic Year", options="Academic Year", reqd=1, in_list_view=1),
	f("term_name", "Data", "Term or Semester"),
	f("status", "Select", "Status", options="Open\nClosed", default="Open"),
	col("cb1"),
	f("grade_level", "Link", "Grade or Year", options="Grade Level"),
	f("section", "Link", "Section", options="Class Section", description="Leave empty for a university course that students register for."),
	f("teacher", "Link", "Teacher", options="Employee", in_list_view=1),
	f("capacity", "Int", "Capacity", description="For courses students register for."),
	f("weekly_hours", "Float", "Hours per Week"),
	sec("sb_sched", "Weekly Schedule"),
	f("schedule", "Table", "Schedule", options="Course Schedule Slot"),
], autoname="hash", title_field="title", icon="fa fa-clock-o", search_fields="subject,teacher,academic_year", perms=perms((MGR, "all"), (REG, "r"), (TCH, "rw"), (ACC, "r")))

# ---------------------------------------------------------------- people
doctype("Guardian", [
	f("guardian_name", "Data", "Name", reqd=1, in_list_view=1),
	f("phone", "Data", "Phone", reqd=1, in_list_view=1),
	f("alt_phone", "Data", "Another Phone"),
	f("email", "Data", "Email", options="Email"),
	col("cb1"),
	f("national_id", "Data", "National ID", in_list_view=1),
	f("job", "Data", "Job"),
	f("customer", "Link", "Customer (Fees Account)", options="Customer", read_only=1, no_copy=1, description="Created automatically: the fees invoices and payments are on it."),
	f("address", "Small Text", "Address"),
], autoname="hash", title_field="guardian_name", icon="fa fa-user", search_fields="guardian_name,phone,national_id", perms=STU())

doctype("Student Guardian", [
	f("guardian", "Link", "Guardian", options="Guardian", reqd=1, in_list_view=1),
	f("guardian_name", "Data", "Name", fetch_from="guardian.guardian_name", read_only=1, in_list_view=1),
	f("relation", "Select", "Relation", options="Father\nMother\nBrother or Sister\nUncle or Aunt\nGrandparent\nOther", default="Father", in_list_view=1),
	f("is_payer", "Check", "Pays the Fees", in_list_view=1),
	f("emergency", "Check", "Emergency Contact"),
], istable=1)

doctype("Scholarship", [
	f("scholarship_name", "Data", "Scholarship", reqd=1, unique=1, in_list_view=1),
	f("discount_pct", "Percent", "Discount (%)", in_list_view=1),
	f("discount_amount", "Currency", "Fixed Discount", in_list_view=1),
	f("active", "Check", "Active", default=1),
	f("reason", "Small Text", "Reason"),
], autoname="field:scholarship_name", icon="fa fa-graduation-cap", perms=MONEY())

doctype("Student", [
	f("student_name", "Data", "Student Name", reqd=1, in_list_view=1),
	f("status", "Select", "Status", options="Active\nGraduated\nWithdrawn\nSuspended\nTransferred", default="Active", in_list_view=1, in_standard_filter=1),
	f("national_id", "Data", "National ID"),
	f("birth_date", "Date", "Date of Birth"),
	f("gender", "Select", "Gender", options="\nMale\nFemale"),
	col("cb1"),
	f("photo", "Attach Image", "Photo"),
	f("admission_date", "Date", "Admission Date", default="Today"),
	f("previous_school", "Data", "Previous School"),
	sec("sb_class", "Class"),
	f("grade_level", "Link", "Grade or Year", options="Grade Level", reqd=1, in_list_view=1, in_standard_filter=1),
	f("stage", "Link", "Stage", options="Education Stage", fetch_from="grade_level.stage", read_only=1, in_standard_filter=1),
	f("institution", "Link", "Institution", options="Education Institution", fetch_from="grade_level.institution", read_only=1),
	col("cb2"),
	f("academic_year", "Link", "Academic Year", options="Academic Year", reqd=1),
	f("section", "Link", "Section", options="Class Section", in_list_view=1),
	sec("sb_guard", "Parents and Guardians"),
	f("guardians", "Table", "Guardians", options="Student Guardian", reqd=1),
	f("payer", "Link", "Pays the Fees", options="Guardian", read_only=1),
	f("customer", "Link", "Fees Customer", options="Customer", read_only=1),
	f("sibling_order", "Int", "Order Among Siblings", read_only=1, description="1 for the eldest child of the payer. Sets the sibling discount."),
	sec("sb_fees", "Fees and Services"),
	f("scholarship", "Link", "Scholarship", options="Scholarship"),
	f("transport_vehicle", "Link", "School Bus", options="Vehicle"),
	sec("sb_health", "Health"),
	f("blood_type", "Select", "Blood Type", options="\nA+\nA-\nB+\nB-\nAB+\nAB-\nO+\nO-"),
	f("medical_notes", "Small Text", "Medical Notes and Allergies"),
], autoname="naming_series:", title_field="student_name", icon="fa fa-graduation-cap", search_fields="student_name,national_id", perms=STU())
DT["Student"]["fields"].insert(0, f("naming_series", "Select", "Series", options="STU-.YYYY.-.####", default="STU-.YYYY.-.####", hidden=1))

doctype("Admission Application", [
	f("applicant_name", "Data", "Applicant Name", reqd=1, in_list_view=1),
	f("status", "Select", "Status", options="New\nUnder Review\nInterview Scheduled\nAccepted\nRejected\nEnrolled\nWithdrawn", default="New", in_list_view=1, in_standard_filter=1),
	f("birth_date", "Date", "Date of Birth"),
	f("gender", "Select", "Gender", options="\nMale\nFemale"),
	f("national_id", "Data", "National ID"),
	f("previous_school", "Data", "Previous School"),
	col("cb1"),
	f("academic_year", "Link", "Academic Year", options="Academic Year", reqd=1),
	f("grade_level", "Link", "Applying For", options="Grade Level", reqd=1, in_list_view=1, in_standard_filter=1),
	f("application_date", "Date", "Application Date", default="Today"),
	f("crm_lead", "Data", "CRM Lead", description="The lead this application came from, if the CRM is used."),
	sec("sb_guard", "Parent or Guardian"),
	f("guardian_name", "Data", "Guardian Name", reqd=1, in_list_view=1),
	f("guardian_phone", "Data", "Phone", reqd=1),
	f("guardian_email", "Data", "Email", options="Email"),
	col("cb2"),
	f("guardian_national_id", "Data", "Guardian National ID"),
	f("guardian", "Link", "Guardian Record", options="Guardian", read_only=1),
	sec("sb_eval", "Interview and Test"),
	f("interview_date", "Datetime", "Interview"),
	f("test_score", "Float", "Entrance Test Score"),
	f("interview_notes", "Small Text", "Notes"),
	sec("sb_reg", "Registration Fee"),
	f("registration_fee", "Currency", "Registration Fee"),
	f("registration_paid", "Check", "Paid", read_only=1),
	f("registration_entry", "Link", "Payment Entry", options="Payment Entry", read_only=1),
	col("cb3"),
	f("student", "Link", "Student", options="Student", read_only=1),
], autoname="naming_series:", title_field="applicant_name", icon="fa fa-file-text-o", search_fields="applicant_name,guardian_name,guardian_phone", perms=STU())
DT["Admission Application"]["fields"].insert(0, f("naming_series", "Select", "Series", options="APP-.YYYY.-.#####", default="APP-.YYYY.-.#####", hidden=1))

# ---------------------------------------------------------------- fees
doctype("Fee Category", [
	f("category_name", "Data", "Fee", reqd=1, unique=1, in_list_view=1, description="Tuition, Books, Uniform, Bus, Activities..."),
	f("income_account", "Link", "Income Account", options="Account", description="Empty: the default fees income account."),
	f("item", "Link", "Invoice Item", options="Item", read_only=1, description="Created automatically."),
], autoname="field:category_name", icon="fa fa-money", perms=MONEY())

doctype("Fee Structure Item", [
	f("fee_category", "Link", "Fee", options="Fee Category", reqd=1, in_list_view=1),
	f("amount", "Currency", "Amount", reqd=1, in_list_view=1),
], istable=1)

doctype("Fee Structure", [
	f("structure_name", "Data", "Name", reqd=1, unique=1, in_list_view=1),
	f("academic_year", "Link", "Academic Year", options="Academic Year", reqd=1, in_list_view=1),
	f("grade_level", "Link", "Grade or Year", options="Grade Level", reqd=1, in_list_view=1),
	f("active", "Check", "Active", default=1),
	col("cb1"),
	f("installments", "Int", "Number of Installments", default=1),
	f("interval_months", "Int", "Months Between Installments", default=1),
	f("down_payment_pct", "Percent", "Down Payment (%)", default=0),
	f("credit_hour_fee", "Currency", "Fee per Credit Hour", description="University: charged for the hours a student registers."),
	sec("sb_items", "Fees"),
	f("items", "Table", "Fees", options="Fee Structure Item", reqd=1),
], autoname="field:structure_name", title_field="structure_name", icon="fa fa-list-alt", perms=MONEY())

doctype("Student Fee Item", [
	f("fee_category", "Link", "Fee", options="Fee Category", reqd=1, in_list_view=1),
	f("description", "Data", "Description", in_list_view=1),
	f("amount", "Currency", "Amount", reqd=1, in_list_view=1),
], istable=1)

doctype("Student Fee", [
	f("student", "Link", "Student", options="Student", reqd=1, in_list_view=1),
	f("student_name", "Data", "Name", fetch_from="student.student_name", read_only=1, in_list_view=1),
	f("academic_year", "Link", "Academic Year", options="Academic Year", reqd=1, in_list_view=1),
	f("fee_structure", "Link", "Fee Structure", options="Fee Structure"),
	col("cb1"),
	f("status", "Select", "Status", options="Draft\nInvoiced\nCancelled", default="Draft", read_only=1, in_list_view=1),
	f("posting_date", "Date", "Date", default="Today", reqd=1),
	f("first_due_date", "Date", "First Installment Date", reqd=1),
	f("customer", "Link", "Customer", options="Customer", read_only=1),
	sec("sb_items", "Fees"),
	f("items", "Table", "Fees", options="Student Fee Item"),
	sec("sb_disc", "Discounts"),
	f("sibling_discount_pct", "Percent", "Sibling Discount (%)"),
	f("scholarship_pct", "Percent", "Scholarship (%)"),
	col("cb2"),
	f("scholarship_amount", "Currency", "Scholarship (fixed)"),
	sec("sb_pay", "Installments"),
	f("installments", "Int", "Number of Installments", default=1),
	f("interval_months", "Int", "Months Between Installments", default=1),
	col("cb3"),
	f("down_payment", "Currency", "Down Payment"),
	sec("sb_tot", "Totals"),
	f("gross", "Currency", "Fees", read_only=1),
	f("sibling_discount", "Currency", "Sibling Discount", read_only=1),
	f("scholarship", "Currency", "Scholarship", read_only=1),
	col("cb4"),
	f("net", "Currency", "After Discounts", read_only=1),
	f("vat", "Currency", "VAT", read_only=1),
	f("total", "Currency", "Invoice Total", read_only=1, in_list_view=1),
	sec("sb_sched", "Installment Schedule"),
	f("schedule_html", "HTML", "Schedule"),
	sec("sb_acc", "Accounting"),
	f("sales_invoice", "Link", "Sales Invoice", options="Sales Invoice", read_only=1, no_copy=1),
], autoname="naming_series:", title_field="student_name", icon="fa fa-file-invoice", search_fields="student,student_name", perms=MONEY())
DT["Student Fee"]["fields"].insert(0, f("naming_series", "Select", "Series", options="FEE-.YYYY.-.#####", default="FEE-.YYYY.-.#####", hidden=1))

# ---------------------------------------------------------------- daily academic work
doctype("Class Attendance Student", [
	f("student", "Link", "Student", options="Student", reqd=1, in_list_view=1),
	f("student_name", "Data", "Name", fetch_from="student.student_name", read_only=1, in_list_view=1),
	f("status", "Select", "Status", options="Present\nAbsent\nLate\nExcused", default="Present", reqd=1, in_list_view=1),
	f("remarks", "Data", "Remarks", in_list_view=1),
], istable=1)

doctype("Class Attendance", [
	f("attendance_date", "Date", "Date", reqd=1, default="Today", in_list_view=1),
	f("section", "Link", "Section", options="Class Section", reqd=1, in_list_view=1),
	f("course_offering", "Link", "Course (optional)", options="Course Offering", description="Leave empty for the daily roll of the whole class."),
	col("cb1"),
	f("taken_by", "Link", "Taken By", options="Employee"),
	f("present_count", "Int", "Present", read_only=1),
	f("late_count", "Int", "Late", read_only=1),
	f("absent_count", "Int", "Absent", read_only=1, in_list_view=1),
	sec("sb_st", "Students"),
	f("students", "Table", "Students", options="Class Attendance Student"),
], autoname="naming_series:", icon="fa fa-check-square-o", perms=CLASS())
DT["Class Attendance"]["fields"].insert(0, f("naming_series", "Select", "Series", options="ATT-.YYYY.-.#####", default="ATT-.YYYY.-.#####", hidden=1))

doctype("Grading Scale Range", [
	f("from_percent", "Percent", "From (%)", reqd=1, in_list_view=1),
	f("grade", "Data", "Grade", reqd=1, in_list_view=1),
	f("points", "Float", "Points", in_list_view=1),
], istable=1)

doctype("Grading Scale", [
	f("scale_name", "Data", "Name", reqd=1, unique=1, in_list_view=1),
	f("ranges", "Table", "Ranges", options="Grading Scale Range", reqd=1),
], autoname="field:scale_name", icon="fa fa-sort-numeric-asc", perms=STRUCT_)

doctype("Mark Sheet Student", [
	f("student", "Link", "Student", options="Student", reqd=1, in_list_view=1),
	f("student_name", "Data", "Name", fetch_from="student.student_name", read_only=1, in_list_view=1),
	f("marks", "Float", "Marks", in_list_view=1),
	f("absent", "Check", "Absent", in_list_view=1),
	f("comment", "Data", "Comment"),
], istable=1)

doctype("Mark Sheet", [
	f("title", "Data", "Title", read_only=1, in_list_view=1),
	f("course_offering", "Link", "Course", options="Course Offering", reqd=1, in_list_view=1),
	f("assessment_type", "Select", "Assessment", options="Quiz\nAssignment\nMidterm\nFinal\nPractical\nOral\nAttendance and Behaviour", reqd=1, in_list_view=1),
	f("assessment_date", "Date", "Date", default="Today"),
	col("cb1"),
	f("max_marks", "Float", "Maximum Marks", reqd=1, default=100),
	f("weight", "Float", "Weight in the Final Result (%)", reqd=1, default=100, description="Marks are weighted by this when the result is added up."),
	f("status", "Select", "Status", options="Draft\nPublished", default="Draft", in_list_view=1),
	sec("sb_st", "Marks"),
	f("students", "Table", "Students", options="Mark Sheet Student"),
], autoname="hash", title_field="title", icon="fa fa-pencil-square-o", perms=CLASS())

doctype("Course Registration Item", [
	f("course_offering", "Link", "Course", options="Course Offering", reqd=1, in_list_view=1),
	f("subject", "Link", "Subject", options="Subject", fetch_from="course_offering.subject", read_only=1, in_list_view=1),
	f("credit_hours", "Float", "Credit Hours", fetch_from="subject.credit_hours", read_only=1, in_list_view=1),
], istable=1)

doctype("Course Registration", [
	f("student", "Link", "Student", options="Student", reqd=1, in_list_view=1),
	f("student_name", "Data", "Name", fetch_from="student.student_name", read_only=1, in_list_view=1),
	f("academic_year", "Link", "Academic Year", options="Academic Year", reqd=1, in_list_view=1),
	f("term_name", "Data", "Term or Semester", reqd=1),
	col("cb1"),
	f("status", "Select", "Status", options="Draft\nConfirmed\nCancelled", default="Draft", in_list_view=1),
	f("total_credit_hours", "Float", "Total Credit Hours", read_only=1, in_list_view=1),
	sec("sb_it", "Courses"),
	f("items", "Table", "Courses", options="Course Registration Item", reqd=1),
], autoname="hash", title_field="student_name", icon="fa fa-list-ol", perms=perms((MGR, "all"), (REG, "all"), (TCH, "r"), (ACC, "r")))

def build():
	os.makedirs(ROOT, exist_ok=True)
	for name, d in DT.items():
		fields = d["fields"]
		order = [x["fieldname"] for x in fields]
		istable = d.get("istable", 0)
		out = {
			"actions": [], "creation": TS, "doctype": "DocType", "engine": "InnoDB", "field_order": order, "fields": fields,
			"links": [], "modified": TS, "modified_by": "Administrator", "module": MODULE, "name": name, "owner": "Administrator",
			"sort_field": "creation", "sort_order": "DESC", "states": [],
			"permissions": [] if istable else d.get("perms", []),
		}
		for k in ("autoname", "title_field", "icon", "track_changes", "issingle", "istable", "show_title_field_in_link", "search_fields"):
			if k in d:
				out[k] = d[k]
		if "autoname" not in d and not istable and not d.get("issingle"):
			out["autoname"] = "hash"
		out["allow_rename"] = 0
		slug = re.sub(r"[^a-z0-9]+", "_", name.lower()).strip("_")
		folder = os.path.join(ROOT, slug)
		os.makedirs(folder, exist_ok=True)
		open(os.path.join(folder, "__init__.py"), "a").close()
		with open(os.path.join(folder, slug + ".json"), "w", encoding="utf-8") as fh:
			json.dump(out, fh, indent=1, ensure_ascii=False)
			fh.write("\n")
		py = os.path.join(folder, slug + ".py")
		if not os.path.exists(py):
			cls = "".join(w.capitalize() for w in re.split(r"[^A-Za-z0-9]+", name))
			with open(py, "w") as fh:
				fh.write(f"from frappe.model.document import Document\n\n\nclass {cls}(Document):\n\tpass\n")


if __name__ == "__main__":
	build()
	print(len(DT), "doctypes")
