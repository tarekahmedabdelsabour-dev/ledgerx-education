# Install

```
cd ~/frappe-bench-v16/apps
git clone <repo-url> ledgerx_education
cd ~/frappe-bench-v16
echo "" >> sites/apps.txt && echo "ledgerx_education" >> sites/apps.txt   # skip if bench get-app is used
./env/bin/pip install -e apps/ledgerx_education
ln -sfn ~/frappe-bench-v16/apps/ledgerx_education/ledgerx_education/public sites/assets/ledgerx_education
bench --site mysite.localhost install-app ledgerx_education
bench --site mysite.localhost migrate && bench --site mysite.localhost clear-cache
```
Then restart the server.

## First setup (Education workspace)
1. **Education Settings:** company, the default fees income account, VAT (usually 0), sibling discounts, default installments.
2. **Education Institution:** one per nursery, school or university branch (each needs a cost center, so each has its own results).
3. **Academic Year** (with terms), then **Education Stage** (Nursery, Primary, Preparatory, Secondary, University), **Grade Level**, **Class Section**.
   University: **Faculty**, **Academic Department**, link the year to its department, and use **Course Offering** + **Course Registration** (credit hours).
4. **Subject**, **Course Offering** (teacher + weekly schedule; a teacher cannot be double-booked).
5. **Fee Category**, **Fee Structure** (per grade and year: fees, installments, down payment %), **Scholarship**.
6. Daily: **Admission Application** (interview, registration fee, accept, enroll) creates the Guardian, the fees Customer and the Student. **Student Fee** invoices the guardian with the installment schedule; **Class Attendance**; **Mark Sheet**.
7. Roles are created automatically: Education Manager, Education Registrar, Education Teacher, Education Accountant. Restrict a teacher to his sections with a User Permission.

## How it is tied to the rest of the app
- Fees are Sales Invoices to the guardian's Customer; payments are Payment Entries; the registration fee stays as an advance and is applied to the first invoice.
- Teachers are Employees (HR): class teacher, course teacher, attendance. Their pay stays in HR.
- A school bus is a Vehicle; the Student, Customer, Employee, Sales Invoice and Payment Entry forms show the related education records.

## Known limits
- Fees are recognised when invoiced (no deferral over the school year).
- A guardian's advances are applied by customer, so unrelated advances may be used against fees.
- Promotion at year end is done by changing grade and section on each student.
- Untested on a live site: only the calculation logic (fees, installments, discounts, grades, attendance) has automated tests.
