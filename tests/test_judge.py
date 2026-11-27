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
        # three reach-in proposals (one card, two scripts) land in ONE cell: counted once
        self.assertEqual((m['cards'], m['scripts'], m['loop_only'], m['in_cells']), (4, 2, 1, 3))
        self.assertEqual(m['ways'], {'bring out': 1, 'witness': 1, 'reach in': 1})
        self.assertAlmostEqual(m['busiest_cell'], 3 / 5)
        self.assertEqual(m['m1'], 'piece × bring out')

    def test_a_map_of_scripts_under_one_primitive_still_reaches_cells(self):
        j = {'proposals': [{'name': 'agent', 'kind': 'card', 'way': 'loop', 'level': 'none'},
                           {'name': 'build', 'kind': 'script', 'way': 'bring out', 'level': 'operation'},
                           {'name': 'diff', 'kind': 'script', 'way': 'witness', 'level': 'operation'}]}
        self.assertEqual(judge.metrics(j, {}, None)['cells'], ['loop', 'operation × bring out', 'operation × witness'])

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
        cells = [f'{lv} × {w}' for lv in judge.LEVELS for w in judge.WAYS] + ['loop']
        (judge.KEYS / 'x.md').write_text('**Filled by:** <name> · <date>\n**M1 accepted:** <cells>\n\n'
                                          '| Cell | Expect | Why |\n|---|---|---|\n'
                                          + ''.join(f'| `{c}` |  |  |\n' for c in cells))
        self.assertIsNone(judge.read_key('x'))

    def test_filled_key_scores_hits_false_positives_and_m1(self):
        (judge.KEYS / 'x.md').write_text(KEY)
        key = judge.read_key('x')
        self.assertEqual(key['cells'], {'piece × bring out': 'propose', 'journey × witness': 'propose',
                                        'operation × reach in': 'leave', 'unit × bring out': 'either'})
        self.assertEqual(key['m1'], ['piece × bring out', 'operation × witness'])
        k = judge.metrics(J, {}, key)['key']
        self.assertEqual((k['hit'], k['want'], k['false'], k['avoid'], k['m1_ok']), (1, 2, 1, 1, True))
        # only designed proposals count for the headline score: J marks none as designed
        kd = judge.metrics(J, {}, key)['key_designed']
        self.assertEqual((kd['hit'], kd['false']), (0, 0))
        jd = dict(J, proposals=[dict(p, designed=True) if p['name'] == 'stories' else p for p in J['proposals']])
        self.assertEqual(judge.metrics(jd, {}, key)['key_designed']['hit'], 1)

    def test_m1_line_written_by_hand(self):
        (judge.KEYS / 'x.md').write_text(KEY.replace('`piece × bring out`, `operation × witness`', 'piece x any, but I am not sure'))
        key = judge.read_key('x')
        self.assertEqual(key['m1'], ['piece × any'])
        self.assertEqual(judge.m1_cell('operation x any ?'), 'operation × any')
        self.assertTrue(judge.metrics(J, {}, key)['key']['m1_ok'])  # J's M1 is piece × bring out
        j = dict(J, m1={'way': 'witness', 'level': 'operation'})
        self.assertFalse(judge.metrics(j, {}, key)['key']['m1_ok'])

    def test_private_key_found_through_its_scenario_dir(self):
        d = Path(self.tmp.name) / 'private'
        d.mkdir()
        (d / 'scenario.json').write_text('{"name": "secret-app", "repo": "x", "commit": "y", "shape": "z", "expected": []}')
        (d / 'answer-key.md').write_text(KEY)
        judge.PRIVATE[:] = [d]
        try:
            self.assertEqual(judge.read_key('secret-app')['m1'], ['piece × bring out', 'operation × witness'])
            self.assertIsNone(judge.read_key('another-app'))
        finally:
            judge.PRIVATE[:] = []

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
