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


def mapdoc(delivered='', candidates='', deferred='', roadmap='', tools='', patterns='', capabilities=''):
    return f"""# Agent map — demo @ abc123 (2026-11-01)

**In one paragraph:** test map.

## Capabilities

{capabilities}

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
        self.assertEqual([x for x in rp.lint(m) if not re.search('Capabilities|Evidence grid|Task mix', x)], [])


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
                         {'states': 'accepted', 'writes': 'proposed', 'test:piece': 'proposed', 'dev-login': 'proposed', 'profile': 'deferred'})
        self.assertEqual(rp.lint(m), [])
        self.assertEqual(len(m['patterns']), 1)
        self.assertEqual({c['id']: c['state'] for c in m['capabilities']}, {'C1': 'accepted', 'C2': 'planned', 'C3': 'planned', 'C4': 'planned'})
        self.assertEqual({c['name']: c['cell'] for c in m['cards']},
                         {'states': ('bring', 'piece'), 'writes': ('witness', 'operation'), 'test:piece': ('bring', 'piece'),
                          'dev-login': ('reach', 'journey'), 'profile': ('reach', 'operation')})
        self.assertEqual(set(m['grid']), set(rp.GRID_LEVELS))
        self.assertTrue(m['task_mix'].startswith('50 commits — 38 behavioural'))


def nodes(page):
    pic = section(page, 'The app and its handles')
    return re.findall(r'data-tip="([^"—]+?) —', pic)


class NoDuplicateNodes(unittest.TestCase):
    def test_one_row_per_verb_is_one_node(self):
        m = rp.parse(mapdoc(tools='| `effect ledger` | egress | check | witness | B6 | `ledger check` |\n'
                                  '| `effect ledger` (replay) | state | steer | bring out | B5 | `ledger replay` |\n'))
        self.assertEqual(nodes(rp.render(m)).count('effect ledger'), 1)
        t = next(t for t in m['tools'] if t['name'] == 'effect ledger')
        self.assertEqual((t['cat'], t['also']), ('egress', ['state']))
        self.assertIn('ledger replay', t['usage'])

    def test_delivered_card_under_another_spelling(self):
        m = rp.parse(mapdoc(delivered=card('bin/agent shot', 'delivered', '**Verified:** demoed — ok\n'),
                            tools='| `bin/agent shot` (scripts/agent/shot.rb) | eyes | see | witness | B1 | `bin/agent shot home` |\n'))
        self.assertEqual(nodes(rp.render(m)).count('bin/agent shot'), 1)

    def test_card_finishing_a_tool_replaces_its_node(self):
        c = card('dev-up', 'proposed').replace('**Finishes:** **New**', '**Finishes:** `make run` (no reset, fixed port)')
        m = rp.parse(mapdoc(candidates=c, tools='| `make run` | launch | steer | reach in | B2 | `make run` |\n'))
        page = rp.render(m)
        self.assertEqual(sorted(nodes(page)), ['dev-up', 'logs'])
        self.assertIn('make run', section(page, 'Already in place'))


ROAD = """### M1 — skeleton
**Status:** {a}
**Builds:** `a`.
**Depends on:** none.
**Demo:** `a`
**Expect:** ok.

### M2 — reach
**Status:** {b}
**Builds:** `b`.
**Depends on:** none.
**Demo:** `b`
**Expect:** ok.
"""


class RoadmapIntro(unittest.TestCase):
    def intro(self, a, b):
        la = 'delivered' if a == 'delivered' else 'proposed'
        lb = 'delivered' if b == 'delivered' else 'proposed'
        v = '**Verified:** demoed — ok\n'
        m = rp.parse(mapdoc(candidates=card('a', la, v if la == 'delivered' else '') + card('b', lb, v if lb == 'delivered' else ''),
                            roadmap=ROAD.format(a=a, b=b)))
        return section(rp.render(m), 'Roadmap')[:1200]

    def test_all_delivered_asks_for_nothing(self):
        t = self.intro('delivered', 'delivered')
        self.assertNotIn('go for', t)
        self.assertIn('Every milestone on this roadmap is delivered', t)

    def test_asks_for_the_next_waiting_milestone(self):
        t = self.intro('delivered', 'proposed')
        self.assertIn('go for M2', t)
        self.assertNotIn('go for M1', t)
        self.assertIn('Delivered: M1', t)

    def test_accepted_is_not_asked_again(self):
        t = self.intro('delivered', 'accepted')
        self.assertNotIn('go for', t)
        self.assertIn('Accepted, being built: M2', t)

    def test_fresh_map_asks_for_m1(self):
        self.assertIn('go for M1', self.intro('proposed', 'proposed'))


CAPS = """| # | Capability — the agent can… | Today | Evidence |
|---|---|---|---|
| C1 | run the loop unattended | a human starts it | `README.md:3` |
| C2 | reach any state as any persona | typed login | B9 |
| C3 | check what left the app | live mail | B6 |
| C4 | replay a production incident | nothing | task "refund bug" |
"""

CAP_ROAD = """### M1 — skeleton
**Capability:** C1 — run the loop unattended.
**Status:** delivered
**Builds:** `a`.
**Depends on:** none.
**Demo:** `a`
**Expect:** ok.
**Verified:** demoed — ran, 2026-11-20

### M2 — reach
**Capability:** reach any state as any persona
**Status:** proposed
**Builds:** `b`.
**Depends on:** none.
**Demo:** `b`
**Expect:** ok.

### M3 — depth
**Capability:** C2 — deeper: time travel.
**Status:** accepted
**Builds:** `c`.
**Depends on:** M2 — `b`.
**Demo:** `c`
**Expect:** ok.

### M4 — stray
**Status:** proposed
**Builds:** `d`.
**Depends on:** none.
**Demo:** `d`
**Expect:** ok.

### Deferred

- C3 — check what left the app: waits for the mail fence.
"""


class Capabilities(unittest.TestCase):
    def setUp(self):
        self.model = rp.parse(mapdoc(
            candidates=card('b', 'proposed') + card('c', 'accepted') + card('d', 'proposed'),
            delivered=card('a', 'delivered', '**Verified:** demoed — ok\n'),
            capabilities=CAPS, roadmap=CAP_ROAD))
        self.page = rp.render(self.model)
        self.caps = {c['id']: c for c in self.model['capabilities']}

    def test_milestones_linked_by_id_or_words(self):
        self.assertEqual({k: [rp.ms_id(m) for m in c['milestones']] for k, c in self.caps.items()},
                         {'C1': ['M1'], 'C2': ['M2', 'M3'], 'C3': [], 'C4': []})

    def test_state_derived_from_milestones(self):
        self.assertEqual({k: c['state'] for k, c in self.caps.items()},
                         {'C1': 'delivered', 'C2': 'accepted', 'C3': 'deferred', 'C4': 'no milestone'})

    def test_roadmap_grouped_by_capability(self):
        road = section(self.page, 'Roadmap')
        self.assertIn('Roadmap — by capability', self.page)
        i = {x: road.index(x) for x in ('>C1<', '>C2<', '>C3<', '>C4<', 'No capability named', 'M4 — stray')}
        self.assertTrue(i['>C1<'] < i['>C2<'] < i['>C3<'] < i['>C4<'] < i['No capability named'] < i['M4 — stray'])
        c2 = road[i['>C2<']:i['>C3<']]
        self.assertIn('M2 — reach', c2)
        self.assertIn('M3 — depth', c2)
        self.assertIn('waits for the mail fence', road[i['>C3<']:i['>C4<']])
        self.assertIn('No milestone delivers this capability', road[i['>C4<']:i['No capability named']])
        self.assertIn('data-key="r0|capability:C1"', road)

    def test_lint(self):
        w = rp.lint(self.model)
        self.assertIn('M4: no **Capability:** — which capability does it deliver?', w)
        self.assertIn('C4: no milestone delivers it and it is not under Deferred', w)
        self.assertFalse([x for x in w if 'names none of' in x])

    def test_unknown_capability_id(self):
        m = rp.parse(mapdoc(capabilities=CAPS, candidates=card('a', 'proposed'),
                            roadmap='### M1 — x\n**Capability:** C9\n**Builds:** `a`.\n**Depends on:** none.\n**Demo:** `a`\n**Expect:** ok.\n'))
        self.assertIn('M1: **Capability:** names none of C1, C2, C3, C4', rp.lint(m))

    def test_overview_counts_capabilities(self):
        page = rp.render([self.model, self.model])
        self.assertIn('<td>1/4 delivered</td>', page)


if __name__ == '__main__':
    unittest.main()


GRID = """## Evidence grid

| Level | Bring out — lab | Witness — effects | Reach in — live |
|---|---|---|---|
| unit — functions | asserted: `bun test` | n/a: pure functions | n/a: nothing to reach |
| piece — screens | gap: no lab | gap: no record of calls | observed: `shot` |
| operation — routes | gap: | gated: `ledger check` | observed: `curl` |
| journey — a session | gap: no e2e | | gap: human login |
"""


def gridmap(grid=GRID, candidates='', mix='**Task mix:** 50 commits — 30 piece.\n'):
    head, _, rest = mapdoc(candidates=candidates, capabilities='| # | Capability — the agent can… | Today | Evidence |\n|---|---|---|---|\n| C1 | x | y | z |\n',
                           roadmap='### M1 — x\n**Capability:** C1\n**Builds:** `lab`.\n**Depends on:** none.\n**Demo:** `x`\n**Expect:** y\n').partition('## Capabilities')
    return head + mix + '\n' + grid + '\n## Capabilities' + rest


def cellcard(name, cell):
    return (f'### `{name}` — lab · B4 Seams · see · {cell} · cost S\n**Status:** proposed\n\n```sh\n$ {name}\nok\n```\n\n')


class EvidenceGrid(unittest.TestCase):
    def test_grid_and_task_mix_read(self):
        m = rp.parse(gridmap())
        self.assertEqual(m['task_mix'], '50 commits — 30 piece.')
        self.assertEqual(rp.grade(m['grid']['operation']['witness']), 'gated')
        self.assertEqual(m['grid']['piece']['label'], 'piece — screens')

    def test_card_cell_from_heading(self):
        m = rp.parse(gridmap(candidates=cellcard('lab', 'bring out at piece') + cellcard('ledger', 'witness at operation')
                             + cellcard('envs', 'loop')))
        self.assertEqual([c['cell'] for c in m['cards']], [('bring', 'piece'), ('witness', 'operation'), None])

    def test_cards_drawn_in_their_cell(self):
        m = rp.parse(gridmap(candidates=cellcard('lab', 'bring out at piece')))
        g = section(rp.render(m), 'Evidence grid')
        row = g[g.index('piece — screens'):]
        row = row[:row.index('</tr>')]
        self.assertIn('lab', row.split('<td')[1])  # the Bring out column of the piece row

    def test_lint_flags_cells_without_verdict(self):
        w = rp.lint(rp.parse(gridmap(candidates=cellcard('lab', 'bring out at piece'))))
        self.assertIn('Evidence grid: no verdict (gated · asserted · observed · gap · n/a) in journey × witness', w)

    def test_lint_flags_card_without_cell_but_not_loop_cards(self):
        m = rp.parse(gridmap(candidates=cellcard('lab', 'bring out') + cellcard('envs', 'loop')))
        self.assertIn('1 card(s) name no cell (`<way> at <level>`): lab', rp.lint(m))

    def test_lint_flags_missing_grid_and_mix(self):
        w = rp.lint(rp.parse(gridmap(grid='', mix='')))
        self.assertTrue(any('no **Evidence grid**' in x for x in w))
        self.assertTrue(any('no **Task mix:**' in x for x in w))

    def test_decisions_bind_the_cards(self):
        grid = GRID.replace('asserted: `bun test` |', 'asserted: `bun test` → leave |') \
                   .replace('gap: no lab |', 'gap: no lab → propose |') \
                   .replace('gated: `ledger check` |', 'gated: `ledger check` → propose |')
        m = rp.parse(gridmap(grid=grid, candidates=cellcard('lab', 'bring out at piece') + cellcard('more-tests', 'bring out at unit')))
        w = rp.lint(m)
        self.assertIn('Evidence grid: decided propose but no card (or deferred card) in operation × witness', w)
        self.assertIn('Evidence grid: a card in a cell decided leave — `more-tests` in unit × bring out', w)
        self.assertTrue(any(x.startswith('Evidence grid: no decision') and 'piece × witness' in x for x in w))
        self.assertEqual(rp.decision('gap: x -> `either`: y'), 'either')

    def test_old_map_without_grid_still_renders(self):
        page = rp.render(rp.parse(mapdoc(candidates=card('a', 'proposed'))))
        self.assertNotIn('<h3>Evidence grid', page)
        self.assertIn('The app and its handles', page)

    def test_tools_row_gets_a_cell_from_its_level_column(self):
        m = rp.parse(mapdoc(tools='| `bun test` | lab | check | bring out | unit | B4 | `bun test` |\n').replace(
            '| Tool | Category | Verb | Way | Point(s) | Usage |\n|---|---|---|---|---|---|',
            '| Tool | Category | Verb | Way | Level | Point(s) | Usage |\n|---|---|---|---|---|---|---|'))
        self.assertEqual({t['name']: t['cell'] for t in m['tools']}['bun test'], ('bring', 'unit'))
