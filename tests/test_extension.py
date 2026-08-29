import unittest
import tempfile
import io
from contextlib import redirect_stdout
from pathlib import Path

from k34cover.cover import cover_k3k4
from k34cover.designs import kirkman, mills, transversal
from k34cover.verify import k3k4cover_checker, optimal_parameters


class SmallAndLegacyTests(unittest.TestCase):
    def test_small_and_new_finite_orders(self):
        for v in (3, 4, 5, 6, 7, 8, 9, 10, 18, 19, 20, 22):
            with self.subTest(v=v):
                r = cover_k3k4(v)
                self.assertTrue(k3k4cover_checker(v, r.blocks))
                xi, a, b = optimal_parameters(v)
                self.assertEqual((len(r.xi), r.n_k3, r.n_k4), (xi, a, b))

    def test_all_residue_branches_through_100_except_17(self):
        # This consecutive sweep is deliberately stronger than one example per
        # congruence class.  Order 17 is a unsupported finite case and is not
        # a recursive ingredient for any larger order.
        for v in range(3, 101):
            if v == 17:
                continue
            with self.subTest(v=v):
                r = cover_k3k4(v)
                self.assertTrue(k3k4cover_checker(v, r.blocks))
                self.assertEqual(
                    (len(r.xi), r.n_k3, r.n_k4),
                    optimal_parameters(v),
                )

    def test_order17_is_explicitly_unsupported(self):
        with self.assertRaises(NotImplementedError):
            cover_k3k4(17)
        with self.assertRaises(NotImplementedError):
            optimal_parameters(17)

    def test_cli_continues_past_unsupported_17(self):
        from k34cover.cli import run
        with tempfile.TemporaryDirectory() as td:
            report = Path(td) / "report.txt"
            with redirect_stdout(io.StringIO()):
                run(16, 21, str(report))
            text = report.read_text()
            self.assertIn("order = 17", text)
            self.assertIn("NOT IMPLEMENTED", text)
            self.assertIn("order = 20", text)
            self.assertIn("check result for K-20:\nTrue", text)


class TransversalTests(unittest.TestCase):
    def test_bck_order12_td(self):
        td = transversal.trans_with_groups(12, 7)
        self.assertEqual(len(td), 144)
        self.assertTrue(all(len(b) == 7 for b in td))

    def test_source_based_finite_tds(self):
        # These are the non-MacNeish bridge ingredients used by Mills'
        # recursive covering construction.
        from collections import Counter
        from itertools import combinations
        cases = ((10,4), (14,4), (21,5), (24,6), (26,4), (38,4), (50,4))
        for r,s in cases:
            with self.subTest(r=r,s=s):
                td = transversal.trans_with_groups(r, s)
                self.assertEqual(len(td), r*r)
                self.assertTrue(all(len(b) == s for b in td))
                mult = Counter()
                for B in td:
                    for x,y in combinations(B,2):
                        gx,gy=(x-1)//r,(y-1)//r
                        self.assertNotEqual(gx,gy)
                        mult[tuple(sorted((x,y)))] += 1
                self.assertTrue(all(c == 1 for c in mult.values()))
                self.assertEqual(len(mult), (s*(s-1)//2)*r*r)


class KirkmanTests(unittest.TestCase):
    def test_pbd_ingredients(self):
        from collections import Counter
        from itertools import combinations
        for m in (22, 34, 46, 70):
            with self.subTest(m=m):
                blocks = kirkman.pbd_for_kirkman(m)
                mult = Counter()
                for B in blocks:
                    mult.update(combinations(B, 2))
                self.assertEqual(len(mult), m*(m-1)//2)
                self.assertTrue(all(c == 1 for c in mult.values()))

    def test_kirkman_systems(self):
        from collections import Counter
        from itertools import combinations
        for v in (9, 15, 21, 45, 69, 93, 141):
            with self.subTest(v=v):
                classes = kirkman.kirkman_triple_system(v)
                self.assertEqual(len(classes), (v-1)//2)
                mult = Counter()
                for cls in classes:
                    self.assertEqual(sorted(x for B in cls for x in B), list(range(1,v+1)))
                    for B in cls:
                        mult.update(combinations(B,2))
                self.assertEqual(len(mult), v*(v-1)//2)
                self.assertTrue(all(c == 1 for c in mult.values()))


class MillsTests(unittest.TestCase):
    def test_explicit_seeds(self):
        seeds = {
            22: mills.k4_seed22,
            31: mills.k4_seed31,
            34: mills.k4_seed34,
            43: mills.k4_seed43,
            55: mills.k4_seed55,
            70: mills.k4_seed70,
            79: mills.k4_seed79,
            82: mills.k4_seed82,
            91: mills.k4_seed91,
            115: mills.k4_seed115,
            127: mills.k4_seed127,
            151: mills.k4_seed151,
            163: mills.k4_seed163,
            199: mills.k4_seed199,
            259: mills.k4_seed259,
        }
        for n, maker in seeds.items():
            with self.subTest(n=n):
                self.assertTrue(mills.check_mills_cover(n, maker()))

    def test_mills_lemma2_and_crs_truncation(self):
        # n=166 exercises the explicit TD(7,12) ingredient.
        for n in (
            58, 67, 103, 106, 118, 130, 139, 154, 166, 175, 187, 202, 211,
            247, 295, 298, 307, 310, 319, 322, 331, 343,
            # First orders at which the adaptive Lemma-2 dispatcher must
            # switch away from a would-be TD(5,33) route.
            418, 427, 439, 442, 451,
        ):
            with self.subTest(n=n):
                self.assertTrue(mills.check_mills_cover(n, mills.mills_k4_cover(n)))
        for v in (
            30, 42, 54, 66, 102, 105, 117, 129, 138, 153, 165, 174, 186,
            201, 210, 246, 294, 297, 306, 309, 318, 321, 330, 342, 417,
            426, 438, 441, 450,
        ):
            with self.subTest(v=v):
                self.assertTrue(k3k4cover_checker(v, cover_k3k4(v).blocks))


class SpectrumRouteTests(unittest.TestCase):
    def test_hole7_route_selector_wide_range(self):
        from k34cover.designs import hole7
        for u in range(0, 10001):
            if u % 4 not in (0, 1):
                continue
            v = 3 * u + 7
            if v in (10, 19):
                continue
            with self.subTest(v=v):
                self.assertTrue(hole7._route_u(u))

    def test_mills_route_selector_wide_range(self):
        # This checks the arithmetic dispatcher without materialising O(n^2)
        # block sets.  It catches gaps between finite seeds and the recursive
        # Lemma-2/3/4 families.
        for n in range(22, 100001):
            if n % 12 not in (7, 10):
                continue
            with self.subTest(n=n):
                self.assertTrue(mills.mills_construction_route(n))


if __name__ == "__main__":
    unittest.main()
