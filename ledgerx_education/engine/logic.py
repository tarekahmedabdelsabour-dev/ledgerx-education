"""Pure calculations (no database), so they can be tested without a site."""
import calendar
from datetime import date, datetime


def r2(x):
	return round(float(x or 0) + 1e-9, 2)


def _d(v):
	if isinstance(v, datetime):
		return v.date()
	if isinstance(v, date):
		return v
	return datetime.strptime(str(v)[:10], "%Y-%m-%d").date()


def add_months(d, n):
	d = _d(d)
	m = d.month - 1 + int(n)
	y, m = d.year + m // 12, m % 12 + 1
	return date(y, m, min(d.day, calendar.monthrange(y, m)[1]))


def sibling_discount_pct(order, pct2=0, pct3=0, pct4=0):
	"""order: 1 for the eldest child of the payer, 2 for the second... Percent off the fees of that child."""
	order = int(order or 1)
	if order <= 1:
		return 0.0
	return float({2: pct2, 3: pct3}.get(order, pct4) or 0)


def fee_totals(amounts, discount_pct=0, scholarship_pct=0, scholarship_amount=0, vat_rate=0):
	"""amounts: price of every fee line. Discounts come off the gross; VAT (if any) is charged on what is left."""
	gross = r2(sum(float(a or 0) for a in amounts))
	d_pct = min(max(float(discount_pct or 0), 0), 100)
	s_pct = min(max(float(scholarship_pct or 0), 0), 100)
	discount = r2(gross * d_pct / 100)
	scholarship = r2(min(gross - discount, (gross - discount) * s_pct / 100 + float(scholarship_amount or 0)))
	net = r2(gross - discount - scholarship)
	vat = r2(net * float(vat_rate or 0) / 100)
	return {"gross": gross, "sibling_discount": discount, "scholarship": scholarship, "net": net, "vat": vat, "total": r2(net + vat)}


def installment_schedule(total, count, first_due, interval_months=1, down_payment=0, today=None):
	"""Down payment due today, then `count` equal installments; the last absorbs the rounding."""
	total, down = r2(total), r2(down_payment)
	if down > total:
		raise ValueError("down payment above the total")
	rows = []
	if down:
		rows.append((_d(today or date.today()), down))
	rest, count = r2(total - down), max(int(count or 1), 1)
	if rest <= 0:
		return rows
	each = r2(rest / count)
	for i in range(count):
		amount = each if i < count - 1 else r2(rest - each * (count - 1))
		rows.append((add_months(first_due, i * int(interval_months or 1)), amount))
	return rows


def grade_for(percent, scale):
	"""scale: rows of (from_percent, grade, points). The highest from_percent not above `percent` wins."""
	best = None
	for frm, grade, points in sorted(scale, key=lambda r: float(r[0])):
		if float(percent) + 1e-9 >= float(frm):
			best = (grade, points)
	return best or (None, 0)


def percent(marks, maximum):
	return r2(float(marks) * 100 / float(maximum)) if float(maximum or 0) else 0.0


def weighted_percent(items):
	"""items: (marks, maximum, weight). Result is the weighted percent over the items that have marks."""
	tw = sum(float(w) for m, mx, w in items if m is not None)
	if not tw:
		return 0.0
	return r2(sum(percent(m, mx) * float(w) for m, mx, w in items if m is not None) / tw)


def attendance_rate(present, late, absent, excused=0):
	"""Late counts as present; excused days are left out of the count."""
	counted = present + late + absent
	return r2((present + late) * 100 / counted) if counted else 100.0


def gpa(rows):
	"""rows: (points, credit_hours)."""
	ch = sum(float(c) for p, c in rows)
	return r2(sum(float(p) * float(c) for p, c in rows) / ch) if ch else 0.0
