"""Regression tests for skills/toolsmith/scripts/review_page.py — status, deferral and roadmap honesty.

    python3 -m unittest discover -s tests
"""
import re, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills/toolsmith/scripts'))
import review_page as rp  # noqa: E402


def card(name, status=None, extra=''):
    st = f'**Status:** {status}\n' if status else ''
    return (f'### `{name}` — runtime · B3 Runtime · steer · reach in · cost S\n{st}'
            f'**Finishes:** **New**\n\n```sh\n$ {name}\nok\n```\n\n**Is:** a CLI.\n{extra}\n')


def mapdoc(delivered='', candidates='', deferred='', roadmap='', tools='', patterns=''):
    return f"""# Agent map — demo @ abc123 (2026-11-01)

**In one paragraph:** test map.

## Tools already in place

| Tool | Category | Verb | Way | Point(s) | Usage |
|---|---|---|---|---|---|
| `logs` | eyes | see | witness | B12 | `tail log` |
{tools}
## Delivered handles

{delivered}
## Candidate handles (not built)

{candidates}
## Deferred handles

{deferred}
## Roadmap

{roadmap}
## Transferable patterns

{patterns}
## Grill

- one?
"""


def section(page, heading):
    """The HTML of the panel whose <h3> starts with heading, up to its </section>."""
    i = page.index(f'<h3>{heading}') if f'<h3>{heading}' in page else page.index(f'>{heading}')
    return page[i:page.index('</section>', i)]


class Lifecycle(unittest.TestCase):
    def setUp(self):
        self.md = mapdoc(
            delivered=card('shot', 'delivered', '**Verified:** demoed — `shot home` wrote shots/home.png, 2026-11-20\n')
            + card('eval', 'delivered', '**Verified:** tested — 6 unit tests pass; live demo deferred: no display\n'),
            candidates=card('login', 'proposed') + card('clock', 'accepted (2026-11-18, M2)')
            + card('press', 'in progress', '**Verified:** implemented — not run yet\n'),
            deferred=card('mail', 'deferred', '**Deferred because:** mail fence first.\n'),
            roadmap="""### M1 — skeleton
**Status:** delivered
**Builds:** `shot`, `eval`.
**Depends on:** none.
**Demo:** `eval run state && shot home`
**Expect:** JSON counts and a PNG.
**Verified:** tested — focused tests pass; live demo deferred: no display on CI

### M2 — reach
**Status:** accepted
**Builds:** `login`, `clock`, `press`.
**Depends on:** M1 — `eval` runs the clock script.
**Demo:** `login --as x && clock +47h`
**Expect:** the reminder banner.

### Deferred

- `mail` — waits for the fence.
""")
        self.model = rp.parse(self.md)
        self.page = rp.render(self.model)
        self.by = {c['name']: c for c in self.model['cards']}

    def test_statuses_read(self):
        self.assertEqual({n: c['life'] for n, c in self.by.items()},
                         {'shot': 'delivered', 'eval': 'delivered', 'login': 'proposed', 'clock': 'accepted',
                          'press': 'in progress', 'mail': 'deferred'})
        self.assertEqual(self.by['shot']['level'], 'demoed')
        self.assertEqual(self.by['eval']['level'], 'tested')
        self.assertEqual(self.by['press']['level'], 'implemented')

    def test_delivered_not_shown_as_proposed(self):
        road = section(self.page, 'Roadmap')
        for n in ('shot', 'eval'):
            self.assertNotIn(f'data-key="r0|card:{n}"', self.page)
            self.assertIn(f'data-key="r0|delivered:{n}"', self.page)
            self.assertNotIn(f'card:{n}', road)
        self.assertIn('Already delivered', road)
        self.assertEqual(self.by['shot']['status'], 'exists')

    def test_tested_never_rounded_up_to_demoed(self):
        dl = section(self.page, 'Delivered')
        self.assertIn('1 of 2 demoed', dl)
        eval_li = dl[dl.index('id="r0-card-1"'):]
        self.assertIn('tested — not demoed', eval_li[:eval_li.index('</li>')])
        m1 = section(self.page, 'Roadmap')
        m1 = m1[m1.index('M1'):m1.index('M2 — reach')]
        self.assertNotIn('demoed end to end', m1)
        self.assertIn('not demoed', m1)

    def test_deferred_separate_from_proposals(self):
        road = section(self.page, 'Roadmap')
        self.assertNotIn('mail', road)
        self.assertNotIn('Not in a milestone', road)
        self.assertIn('data-key="r0|deferred:mail"', section(self.page, 'Deferred'))
        self.assertNotIn('data-tip="mail', section(self.page, 'The app and its handles'))

    def test_open_work_carries_its_status(self):
        road = section(self.page, 'Roadmap')
        self.assertIn('data-key="r0|card:clock"', road)
        self.assertIn('<span class="life accepted">accepted</span>', road)
        self.assertIn('<span class="life in-progress">in progress</span>', road)

    def test_dependencies_shown_as_stated(self):
        road = section(self.page, 'Roadmap')
        m1, m2 = road.split('M2 — reach', 1)
        self.assertIn('independent', m1)
        self.assertIn('depends on M1', m2)

    def test_lint_flags_delivered_not_demoed_only(self):
        w = rp.lint(self.model)
        self.assertEqual([x for x in w if 'not demoed' in x], ['M1: delivered but not demoed (tested) — shown as such'])
        self.assertFalse([x for x in w if 'Status' in x or 'Depends' in x or 'Demo' in x])


class Milestones(unittest.TestCase):
    def test_missing_depends_demo_expect(self):
        m = rp.parse(mapdoc(candidates=card('a', 'proposed') + card('b', 'proposed'), roadmap="""### M1 — a
**Builds:** `a`.
**Demo:** `a`

### M2 — b
**Builds:** `b`.
"""))
        page, w = rp.render(m), rp.lint(m)
        road = section(page, 'Roadmap')
        self.assertEqual(road.count('dependencies not stated'), 2)
        self.assertIn('No demo', road)
        self.assertIn('No expected result', road)
        self.assertIn('M1, M2: no **Depends on:** — the numbers will be read as dependencies', w)
        self.assertIn('M2: no **Demo:**', w)
        self.assertIn('M1: no **Expect:** — the demo has no observable result to check', w)

    def test_old_one_line_format_still_reads(self):
        m = rp.parse(mapdoc(candidates=card('a') + card('b') + card('c'), roadmap="""### M1 — a
**Builds:** `a`. **Demo:** run a.

### M2 — b
**Builds:** `b`, scripts `x`. **Demo:** run b.

**Deferred:** `c` — later.
"""))
        ms = m['roadmap']['milestones']
        self.assertEqual([x['builds'] for x in ms], ['`a`.', '`b`, scripts `x`.'])
        self.assertEqual([x['demo'] for x in ms], ['run a.', 'run b.'])
        self.assertEqual({c['name']: c['life'] for c in m['cards']}, {'a': 'proposed', 'b': 'proposed', 'c': 'deferred'})
        self.assertTrue(any('without a **Status:**' in x for x in rp.lint(m)))

    def test_deferred_none_does_not_defer_a_built_card(self):
        m = rp.parse(mapdoc(candidates=card('a', 'proposed'), roadmap="""### M1 — a
**Builds:** `a`.
**Depends on:** none.
**Demo:** `a`
**Expect:** ok.

**Deferred:** none. `a`'s write path is deferred indefinitely, which is a deny, not a build.
"""))
        self.assertEqual(m['cards'][0]['life'], 'proposed')
        self.assertEqual(m['roadmap']['deferred'], [])
        self.assertEqual(rp.lint(m), [])


class AfterTheSnapshot(unittest.TestCase):
    """Handles delivered after the map's commit stamp: the map is edited, not re-made."""

    def test_delivered_card_also_added_to_tools_is_shown_once(self):
        m = rp.parse(mapdoc(delivered=card('shot', 'delivered', '**Verified:** demoed — ran it.\n'),
                            tools='| `shot` | eyes | see | witness | B1 | `shot home` |\n'))
        self.assertEqual([t['name'] for t in m['tools']], ['logs'])
        self.assertEqual(rp.render(m).count('data-tip="shot'), 1)

    def test_proposed_card_finishing_a_tool_keeps_the_tool(self):
        m = rp.parse(mapdoc(candidates=card('logs', 'proposed'), roadmap=''))
        self.assertEqual([t['name'] for t in m['tools']], ['logs'])

    def test_delivered_left_under_candidates_is_still_delivered(self):
        m = rp.parse(mapdoc(candidates=card('shot', 'built', '**Verified:** demoed — ok\n') + card('b', 'proposed'),
                            roadmap='### M1 — x\n**Builds:** `shot`, `b`.\n**Depends on:** none.\n**Demo:** `b`\n**Expect:** ok.\n'))
        page = rp.render(m)
        self.assertEqual(m['cards'][0]['life'], 'delivered')
        self.assertIn('data-key="r0|delivered:shot"', page)
        self.assertNotIn('card:shot', section(page, 'Roadmap'))

    def test_delivered_without_evidence_is_flagged(self):
        m = rp.parse(mapdoc(delivered=card('shot', 'delivered')))
        self.assertIn('delivered card `shot` has no **Verified:** level (implemented · tested · demoed)', rp.lint(m))
        self.assertIn('delivered without evidence', rp.render(m))


class Patterns(unittest.TestCase):
    def test_patterns_table(self):
        m = rp.parse(mapdoc(patterns="""| Pattern | Does | Evidence here | Fits when | Does not fit when | Here as |
|---|---|---|---|---|---|
| test-impact | runs reachable tests | `bin/test:12` | cheap graph | dynamic plugins | `test --changed` |
"""))
        self.assertEqual(m['patterns'], [['test-impact', 'runs reachable tests', '`bin/test:12`', 'cheap graph', 'dynamic plugins', '`test --changed`']])
        self.assertIn('data-key="r0|patterns:section"', rp.render(m))


class Template(unittest.TestCase):
    def test_template_renders_clean(self):
        m = rp.parse((ROOT / 'skills/toolsmith/references/map-template.md').read_text())
        self.assertEqual({c['name']: c['life'] for c in m['cards']},
                         {'dev-login': 'proposed', 'remote eval': 'accepted', 'mail last': 'deferred'})
        self.assertEqual(rp.lint(m), [])
        self.assertEqual(len(m['patterns']), 1)


if __name__ == '__main__':
    unittest.main()
