"""The insight desk adapter, the sheet checks and the spec propose --insight hook.
Synthetic fixtures only: no sheet here is a real one, and nothing touches the network."""
import contextlib
import copy
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import types
import unittest

import growth
from engine import cli, insight_sheet, spec

ROOT = Path(growth.HERE)
EXAMPLE = ROOT / 'specs' / 'examples' / 'synthetic-week.json'
U4 = {'urgency': 4, 'current': None}
SKILL = Path(os.environ.get('INSIGHT_DESK_SKILL', '/home/user/ai-harness/candidates/insight-desk'))


def _test(reason, **extra):
    return {'result': 'pass', 'reason': reason, **extra}


def idea(idea_id, level='measurement', method='instrument-first'):
    return {'id': idea_id, 'claim': f'Synthetic claim for {idea_id}: a shared clip names who sent it.',
            'mechanic': 'Synthetic mechanic: the share link carries the sender so the first listen is joined.',
            'idea_level': level, 'method': method, 'channel_role': 'the vertical master on the push channels',
            'conversion_path': {'offer': 'the free show', 'link': 'tracked() link from the creative id',
                                'why_act': 'the mate who sent it is named in the clip'},
            'kill_condition': 'No joined listens after two matchweeks.',
            'tests': {'specificity': _test('Swapped in a named rival app; the pundit row no longer exists there.'),
                      'share': _test('A fan sends it to the mate who argued the other side, adding one line.'),
                      'analogue': _test('A public referral link that names the sender, read today.',
                                        url='https://example.com/analogue', read_at='2026-11-24'),
                      'floor': _test('Read COPY.md and invariants/registry.json; closest rule is tracked links only.'),
                      'kill_the_favourite': _test('Attack: fans will not share. Answer: it measures exactly that.')}}


def sheet(**change):
    value = {'schema': 'insight-sheet/1', 'venture': 'fulltime', 'repo': 'krishanraja/growth-fulltime',
             'harness_skill_sha': '0' * 40, 'made_at': '2026-11-24T09:00:00Z',
             'north_star': {'metric': 'attributed_new_completers', 'urgency': 4, 'current': None, 'as_of': None},
             'stall_check': {'diagnosis': 'measurement', 'evidence': 'Synthetic: NOW.md says the number is unmeasured.'},
             'insights': [{'audience': 'fans who argue about a match', 'wants': 'to win the argument',
                           'but': 'they cannot show who said it first', 'because': 'clips carry no sender',
                           'assumption': True}],
             'chosen_insight': 0,
             'discarded_obvious': ['A highlights reel', 'A discount', 'A countdown to kick off'],
             'ideas': [idea('named-sender'), idea('first-listen-join', method='one-variable-test')],
             'consults': [{'engine': 'divergent-thinker', 'op': 'score', 'result': 'unavailable',
                           'ref': 'no connector in this run'}],
             'lead': 'named-sender',
             'blind_passes': [{'reader': 'reader-a', 'order': ['named-sender', 'first-listen-join'], 'lead': 'named-sender'},
                              {'reader': 'reader-b', 'order': ['first-listen-join', 'named-sender'], 'lead': 'named-sender'}]}
    value.update(change)
    value['sheet_sha256'] = insight_sheet.sheet_sha(value)
    return value


class Adapter(unittest.TestCase):
    def test_the_committed_adapter_holds(self):
        self.assertEqual(insight_sheet.adapter_errors(insight_sheet.load_adapter()), [])

    def test_the_adapter_refuses_humour_and_a_wrong_namespace(self):
        adapter = insight_sheet.load_adapter()
        bad = copy.deepcopy(adapter)
        bad['humour']['allowed'] = True
        self.assertTrue(any('humour' in e for e in insight_sheet.adapter_errors(bad)))
        bad = copy.deepcopy(adapter)
        bad['divergent']['namespace'] = 'growth-heartside:ideas'
        self.assertTrue(any('growth-fulltime:ideas' in e for e in insight_sheet.adapter_errors(bad)))
        bad = copy.deepcopy(adapter)
        bad['sheets'] = 'docs/insight/'
        self.assertTrue(any('local/' in e for e in insight_sheet.adapter_errors(bad)))
        bad = copy.deepcopy(adapter)
        bad['first_sheet']['idea_level'] = 'campaign'
        self.assertTrue(any('measurement' in e for e in insight_sheet.adapter_errors(bad)))

    def test_now_state_reads_the_north_star_line(self):
        state = insight_sheet.now_state()
        self.assertIsInstance(state, dict)
        self.assertIn('urgency', state)


class Sheet(unittest.TestCase):
    def test_a_synthetic_measurement_sheet_is_valid_at_u4(self):
        self.assertEqual(insight_sheet.validate(sheet(), state=U4), [])

    def test_at_u4_unmeasured_only_measurement_ideas(self):
        value = sheet(ideas=[idea('named-sender', level='campaign'), idea('first-listen-join')],
                      stall_check={'diagnosis': 'idea', 'evidence': 'synthetic'})
        errors = insight_sheet.validate(value, state=U4)
        self.assertTrue(any('measurement' in e and 'named-sender' in e for e in errors))

    def test_engine_reads_urgency_from_now_md_not_the_sheet(self):
        value = sheet(north_star={'metric': 'attributed_new_completers', 'urgency': 3, 'current': 5, 'as_of': None},
                      ideas=[idea('named-sender', level='campaign'), idea('first-listen-join', level='campaign')],
                      stall_check={'diagnosis': 'idea', 'evidence': 'synthetic'})
        self.assertEqual(insight_sheet.skill_errors(value), [])
        errors = insight_sheet.engine_errors(value, state=U4)
        self.assertTrue(any('NOW.md says U4' in e for e in errors))
        self.assertTrue(any('measurement ideas only' in e for e in errors))

    def test_humour_consult_and_another_venture_are_refused(self):
        value = sheet(consults=[{'engine': 'humour-engine', 'op': 'check', 'result': 'pass', 'ref': 'x'}])
        self.assertTrue(any('humour engine is unavailable' in e for e in insight_sheet.validate(value, state=U4)))
        value = sheet(venture='heartside', repo='krishanraja/growth-heartside')
        self.assertTrue(any('not this engine' in e for e in insight_sheet.validate(value, state=U4)))

    def test_skill_rules_hold(self):
        tampered = sheet()
        tampered['lead'] = 'first-listen-join'
        self.assertTrue(any('sheet_sha256' in e for e in insight_sheet.validate(tampered, state=U4)))
        scored = sheet(consults=[])
        scored['ideas'][0]['tests']['share']['score'] = 9
        scored['sheet_sha256'] = insight_sheet.sheet_sha(scored)
        self.assertTrue(any('no scores' in e or 'unexpected fields' in e
                            for e in insight_sheet.validate(scored, state=U4)))
        split = sheet(blind_passes=[
            {'reader': 'reader-a', 'order': ['named-sender', 'first-listen-join'], 'lead': 'named-sender'},
            {'reader': 'reader-b', 'order': ['first-listen-join', 'named-sender'], 'lead': 'first-listen-join'}])
        self.assertTrue(any('same lead' in e for e in insight_sheet.validate(split, state=U4)))
        stalled = sheet(stall_check={'diagnosis': 'distribution', 'evidence': 'synthetic'})
        self.assertTrue(any('not the idea' in e for e in insight_sheet.validate(stalled, state=U4)))
        no_path = sheet()
        no_path['ideas'][1]['conversion_path'] = {'offer': 'x', 'link': '', 'why_act': 'y'}
        no_path['sheet_sha256'] = insight_sheet.sheet_sha(no_path)
        self.assertTrue(any('conversion path' in e for e in insight_sheet.validate(no_path, state=U4)))
        unread = sheet()
        unread['ideas'][0]['tests']['analogue'] = {'result': 'unavailable', 'reason': 'none found',
                                                   'url': None, 'read_at': None}
        unread['sheet_sha256'] = insight_sheet.sheet_sha(unread)
        self.assertTrue(any('leads only when every test passed' in e
                            for e in insight_sheet.validate(unread, state=U4)))
        obvious = sheet()
        obvious['ideas'][1]['claim'] = 'A highlights reel'
        obvious['sheet_sha256'] = insight_sheet.sheet_sha(obvious)
        self.assertTrue(any('discarded obvious' in e for e in insight_sheet.validate(obvious, state=U4)))

    def test_no_readable_now_md_stops_at_the_gate(self):
        self.assertTrue(any('north-star-state' in e for e in insight_sheet.engine_errors(sheet(), state=None)))

    @unittest.skipUnless((SKILL / 'references' / 'methods-by-category.md').exists(), 'no local ai-harness checkout')
    def test_methods_are_checked_against_the_skill_when_a_checkout_is_at_hand(self):
        methods = insight_sheet.methods_from(SKILL)
        self.assertEqual(insight_sheet.validate(sheet(), state=U4, methods=methods), [])
        value = sheet(ideas=[idea('named-sender', method='made-up-method'), idea('first-listen-join')])
        self.assertTrue(any('made-up-method' in e for e in insight_sheet.validate(value, state=U4, methods=methods)))

    @unittest.skipUnless((SKILL / 'scripts' / 'tests' / 'fixtures' / 'sample-sheet.json').exists(),
                         'no local ai-harness checkout')
    def test_the_skills_own_sample_sheet_passes_the_skill_rules_here(self):
        sample = insight_sheet.load_json(SKILL / 'scripts' / 'tests' / 'fixtures' / 'sample-sheet.json')
        self.assertEqual(insight_sheet.skill_errors(sample, insight_sheet.methods_from(SKILL)), [])


class Seed(unittest.TestCase):
    def campaign(self, with_objective=True):
        value = spec.load(EXAMPLE)
        if with_objective:
            value['objectives'].append({'key': 'attributed_new_completers', 'target': 30})
        return value

    def test_seed_needs_the_objective_the_lead_is_measured_by(self):
        with self.assertRaisesRegex(ValueError, 'attributed_new_completers'):
            insight_sheet.seed(self.campaign(False), sheet(), state=U4)
        found = insight_sheet.seed(self.campaign(), sheet(), state=U4)
        self.assertEqual((found['lead'], found['idea_level'], found['objective_key']),
                         ('named-sender', 'measurement', 'attributed_new_completers'))

    def test_no_lead_is_not_seeded(self):
        with self.assertRaisesRegex(ValueError, 'no lead'):
            insight_sheet.seed(self.campaign(), sheet(lead=None), state=U4)

    def test_the_proposal_binds_the_same_spec_with_or_without_a_sheet(self):
        value = self.campaign()
        plain = spec.proposal(value, '2026-11-30T08:00:00+00:00')
        seeded = spec.proposal(value, '2026-11-30T08:00:00+00:00',
                               insight=insight_sheet.seed(value, sheet(), state=U4))
        self.assertEqual(plain['payload_sha256'], seeded['payload_sha256'])
        self.assertEqual(plain['exact_payload'], seeded['exact_payload'])
        self.assertEqual((seeded['stage'], seeded['wall']), ('plan', 'strategy'))
        self.assertIn('named-sender', seeded['why'])
        self.assertEqual(len(seeded['evidence']), len(plain['evidence']) + 1)
        self.assertEqual(plain, spec.proposal(value, '2026-11-30T08:00:00+00:00', insight=None))


class Hook(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.growth = types.SimpleNamespace(LOCAL=str(self.tmp / 'local'), HERE=str(ROOT),
                                            load_state=lambda: {}, read_rail=lambda: [])

    def write(self, name, value):
        path = self.tmp / name
        path.write_text(json.dumps(value), encoding='utf-8')
        return str(path)

    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        code = 0
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            try:
                cli.main(list(argv), self.growth)
            except SystemExit as stop:
                code = stop.code
        text = out.getvalue()
        try:
            body = json.loads(text)
        except ValueError:
            body = text
        return code, body, err.getvalue()

    def propose(self, path, *extra):
        return self.run_cli('spec', 'propose', path, '--expires-at', '2026-11-30T08:00:00+00:00', *extra)

    def campaign(self):
        value = spec.load(EXAMPLE)
        value['objectives'].append({'key': 'attributed_new_completers', 'target': 30})
        return self.write('spec.json', value)

    def test_without_insight_the_output_is_unchanged(self):
        path = self.campaign()
        code, body, _ = self.propose(path)
        self.assertEqual(code, 0)
        self.assertEqual(set(body), {'prepared', 'sent', 'proposal'})
        self.assertNotIn('Seeded by insight sheet', body['proposal']['why'])

    def test_with_insight_the_live_now_md_decides(self):
        state = insight_sheet.now_state(ROOT)
        path = self.campaign()
        value = sheet(north_star={'metric': 'attributed_new_completers', 'urgency': state['urgency'],
                                  'current': state['current'], 'as_of': None})
        if state['urgency'] == 4 and state['current'] is None:
            code, body, _ = self.propose(path, '--insight', self.write('sheet.json', value))
            self.assertEqual(code, 0)
            self.assertIs(body['sent'], False)
            self.assertEqual(body['insight']['lead'], 'named-sender')
            self.assertIn('Seeded by insight sheet', body['proposal']['why'])
        bad = sheet(venture='heartside', repo='krishanraja/growth-heartside')
        code, _, err = self.propose(path, '--insight', self.write('bad.json', bad))
        self.assertEqual(code, 1)
        self.assertIn('not this engine', err)

    def test_insight_goes_with_propose_only(self):
        code, _, err = self.run_cli('spec', 'check', self.campaign(), '--insight', self.write('sheet.json', sheet()))
        self.assertEqual(code, 1)
        self.assertIn('spec propose only', err)


if __name__ == '__main__':
    unittest.main()
