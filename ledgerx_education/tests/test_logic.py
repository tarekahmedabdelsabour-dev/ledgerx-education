"""Pure-logic tests: python3 -m unittest discover -s ledgerx_education/tests (no site needed)."""
import importlib.util
import os
import unittest

_p = os.path.join(os.path.dirname(__file__), "..", "engine", "logic.py")
_s = importlib.util.spec_from_file_location("education_logic", _p)
L = importlib.util.module_from_spec(_s)
_s.loader.exec_module(L)


class T(unittest.TestCase):
	def test_sibling(self):
		self.assertEqual([L.sibling_discount_pct(i, 10, 15, 20) for i in (1, 2, 3, 4, 6)], [0, 10, 15, 20, 20])

	def test_fee_totals(self):
		t = L.fee_totals([30000, 5000, 1000], 10, 20, 0, 0)
		self.assertEqual((t["gross"], t["sibling_discount"], t["scholarship"], t["net"], t["total"]), (36000, 3600, 6480, 25920, 25920))
		t = L.fee_totals([1000], 0, 0, 5000, 14)
		self.assertEqual((t["scholarship"], t["net"], t["vat"]), (1000, 0, 0))

	def test_schedule_adds_up(self):
		rows = L.installment_schedule(10000, 3, "2026-09-01", 1, 1000, "2026-08-20")
		self.assertEqual(round(sum(a for _d, a in rows), 2), 10000)
		self.assertEqual([str(d) for d, _a in rows], ["2026-08-20", "2026-09-01", "2026-10-01", "2026-11-01"])
		self.assertEqual([a for _d, a in rows], [1000, 3000, 3000, 3000])
		rows = L.installment_schedule(100, 3, "2026-09-30", 1)
		self.assertEqual(round(sum(a for _d, a in rows), 2), 100)
		self.assertEqual(str(rows[1][0]), "2026-10-30")
		self.assertEqual(str(L.installment_schedule(100, 2, "2026-01-31")[1][0]), "2026-02-28")

	def test_grades(self):
		scale = [(0, "F", 0), (50, "D", 1), (65, "C", 2), (75, "B", 3), (85, "A", 4)]
		self.assertEqual(L.grade_for(49.9, scale), ("F", 0))
		self.assertEqual(L.grade_for(85, scale), ("A", 4))
		self.assertEqual(L.grade_for(70, scale), ("C", 2))

	def test_weighted_and_attendance(self):
		self.assertEqual(L.weighted_percent([(18, 20, 20), (40, 50, 30), (None, 100, 50)]), 84.0)
		self.assertEqual(L.weighted_percent([]), 0.0)
		self.assertEqual(L.attendance_rate(8, 1, 1, 3), 90.0)
		self.assertEqual(L.attendance_rate(0, 0, 0), 100.0)
		self.assertEqual(L.gpa([(4, 3), (2, 3), (3, 4)]), 3.0)


if __name__ == "__main__":
	unittest.main()
