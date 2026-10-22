import unittest
from dk_scoring import score_observed_offense, dst_demo_estimate

class ScoringTests(unittest.TestCase):
    def test_bonus_and_reception(self):
        stats = dict(passing_yards=300, passing_tds=2, passing_interceptions=1,
                     rushing_yards=100, rushing_tds=1, receiving_yards=100,
                     receiving_tds=1, receptions=5, fumbles_lost=1)
        score, missing = score_observed_offense(stats)
        self.assertEqual(missing, [])
        self.assertAlmostEqual(score, 64.0)

    def test_missing_stats_not_assumed_zero(self):
        score, missing = score_observed_offense({'passing_yards': 300})
        self.assertIsNone(score)
        self.assertIn('fumbles_lost', missing)

    def test_dst_baseline(self):
        self.assertEqual(dst_demo_estimate(7.456), 7.46)
        self.assertIsNone(dst_demo_estimate(None))

if __name__ == '__main__':
    unittest.main()
