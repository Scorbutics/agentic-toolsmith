"""Tests for evals/judge.py — the parts that need no model: keys, metrics, agreement, labels, paths.

    python3 -m unittest discover -s tests
"""
import sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'evals'))
import judge  # noqa: E402

J = {'proposals': [
    {'name': 'agent run', 'kind': 'card', 'way': 'reach in', 'level': 'operation'},
    {'name': 'clock', 'kind': 'script', 'way': 'reach in', 'level': 'operation'},
    {'name': 'state', 'kind': 'script', 'way': 'reach in', 'level': 'operation'},
    {'name': 'stories', 'kind': 'card', 'way': 'bring out', 'level': 'piece'},
    {'name': 'writes', 'kind': 'card', 'way': 'witness', 'level': 'operation'},
    {'name': 'envs up', 'kind': 'card', 'way': 'loop', 'level': 'none'},
], 'm1': {'name': 'stories', 'way': 'bring out', 'level': 'piece'}, 'author_tools': {'motu': 'absent', 'assay': 'proposed'}}

KEY = """# Answer key — x

**Filled by:** someone · 2026-11-25
**M1 accepted:** `piece × bring out`, `operation × witness`

| Cell | Expect (`propose` · `leave` · `either`) | Why |
|---|---|---|
| `piece × bring out` | propose | 20 screens |
| `journey × witness` | propose | mail |
| `operation × reach in` | leave | covered by the API tests |
| `unit × bring out` | either | |
| `loop` |  |  |
"""


class Metrics(unittest.TestCase):
    def test_scripts_counted_apart_from_cards(self):
        m = judge.metrics(J, {}, None)
        self.assertEqual((m['cards'], m['scripts'], m['loop_only'], m['in_cells']), (4, 2, 1, 3))
        self.assertEqual(m['ways'], {'bring out': 1, 'witness': 1, 'reach in': 1})
        self.assertEqual(m['m1'], 'piece × bring out')

    def test_author_tool_misfit_only_outside_the_fit_list(self):
        self.assertEqual(judge.metrics(J, {}, None)['author_misfit'], ['assay'])
        self.assertEqual(judge.metrics(J, {'author_tools_fit': ['assay']}, None)['author_misfit'], [])

    def test_old_judgments_without_kind_count_as_cards(self):
        old = {'proposals': [{'name': 'a', 'way': 'reach in', 'level': 'journey'}]}
        self.assertEqual(judge.metrics(old, {}, None)['cards'], 1)


class Keys(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        judge.KEYS = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_empty_template_is_not_a_key(self):
        (judge.KEYS / 'x.md').write_text((ROOT / 'evals/answer-keys/miniflux.md').read_text())
        self.assertIsNone(judge.read_key('x'))

    def test_filled_key_scores_hits_false_positives_and_m1(self):
        (judge.KEYS / 'x.md').write_text(KEY)
        key = judge.read_key('x')
        self.assertEqual(key['cells'], {'piece × bring out': 'propose', 'journey × witness': 'propose',
                                        'operation × reach in': 'leave', 'unit × bring out': 'either'})
        self.assertEqual(key['m1'], ['piece × bring out', 'operation × witness'])
        k = judge.metrics(J, {}, key)['key']
        self.assertEqual((k['hit'], k['want'], k['false'], k['avoid'], k['m1_ok']), (1, 2, 1, 1, True))

    def test_every_template_lists_the_twelve_cells_and_loop(self):
        for p in (ROOT / 'evals/answer-keys').glob('*.md'):
            if p.name == 'README.md':
                continue
            text = p.read_text()
            for lv in judge.LEVELS:
                for w in judge.WAYS:
                    self.assertIn(f'`{lv} × {w}`', text, p.name)
            self.assertIn('`loop`', text)


class Agreement(unittest.TestCase):
    def test_identical_judgments_agree(self):
        m = judge.metrics(J, {}, None)
        a = judge.agreement(m, m)
        self.assertEqual((a['m1_same'], a['cells_jaccard'], a['way_share_gap']), (True, 1.0, 0.0))

    def test_different_m1_and_cells(self):
        other = dict(J, m1={'way': 'loop'}, proposals=J['proposals'][:1])
        a = judge.agreement(judge.metrics(J, {}, None), judge.metrics(other, {}, None))
        self.assertFalse(a['m1_same'])
        self.assertLess(a['cells_jaccard'], 1.0)


class Paths(unittest.TestCase):
    def test_single_and_repeated_layouts(self):
        self.assertEqual(judge.where(Path('root/miniflux/sonnet/skill/map.md')), ('miniflux', 'sonnet', 'skill', 1))
        self.assertEqual(judge.where(Path('root/miniflux/haiku/baseline/r3/map.md')), ('miniflux', 'haiku', 'baseline', 3))


class Labels(unittest.TestCase):
    def test_sheet_round_trip(self):
        with tempfile.TemporaryDirectory() as d:
            mp = Path(d) / 'map.md'
            mp.write_text('# map')
            (Path(d) / 'judge.json').write_text(__import__('json').dumps(J))
            sheet = judge.label_sheet(mp, 'sonnet')
            self.assertIsNone(judge.read_labels(sheet))  # untouched sheet: no labels yet
            text = sheet.read_text().replace('| stories | card | bring out | piece |  |  |  |',
                                             '| stories | card | bring out | piece |  | reach in |  |')
            sheet.write_text(text.replace('**Your M1:**', '**Your M1:** piece × reach in'))
            h = judge.human_agreement(J, judge.read_labels(sheet))
            self.assertAlmostEqual(h['cells_same'], 5 / 6)
            self.assertFalse(h['m1_same'])


if __name__ == '__main__':
    unittest.main()
