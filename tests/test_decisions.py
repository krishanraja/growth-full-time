"""Reading Krish's decisions on main's report (Ruling, Krish, 2026-11-15: Full Time v2
lands on main keeping main's Control Center report): his amended version counts only
when amended_sha256 checks, an approved go-live is an instruction for him and never an
action, his answers are kept once each, and a protocol major other than 1 is refused.
Every fixture is synthetic; the stand-in listens on 127.0.0.1 only."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from engine import control_center as cc
from engine import reporting
from tests.test_control_center import TOKEN, StandIn, sample_report


def his_digest(amount, words):
    """amended_sha256 as Control Center computes it, written apart from the engine."""
    body = json.dumps({'amount_usd': amount, 'exact_payload': words}, sort_keys=True,
                      separators=(',', ':'), ensure_ascii=False)
    return hashlib.sha256(body.encode('utf-8')).hexdigest()


def post():
    return reporting._proposal('fulltime:post:YT_SYNTH_GO', 'youtube: YT_SYNTH_GO', 'Ready.', 'prepared', 'post',
                               {'channel': 'youtube', 'exact_payload': 'Engine words.', 'target': 'YT_SYNTH_GO'},
                               'creative_published', 'YT_SYNTH_GO', channel='youtube', exact_payload='Engine words.')


def spend(amount=20):
    return reporting._proposal('fulltime:spend:2026-W44', 'Credits, 2026-W44', 'Synthetic credits.', 'prepared',
                               'spend', {'amount_usd': amount}, 'spend_recorded', '2026-W44', amount_usd=amount)


def decision(proposal, **extra):
    return {'proposal_id': proposal['proposal_id'], 'decision': 'approved', 'decided_at': '2026-10-27T08:00:00Z',
            'payload_sha256': proposal['payload_sha256'], 'amended': False, **extra}


class AmendmentTests(unittest.TestCase):
    def test_his_verified_version_is_what_he_approved(self):
        proposal = post()
        decided = cc.classify([decision(proposal, amended=True, exact_payload='His words.', amount_usd=None,
                                        amended_sha256=his_digest(None, 'His words.'))], [proposal])
        self.assertEqual((decided['approved_amended'], decided['approved_current']), ([proposal['proposal_id']], []))
        approved = decided['approved'][proposal['proposal_id']]
        self.assertEqual((approved['exact_payload'], approved['amended'], approved['sha256']),
                         ('His words.', True, his_digest(None, 'His words.')))
        self.assertIn('amended version', decided['instructions'][0]['line'])

    def test_an_amended_amount_is_his_amount(self):
        proposal = spend(amount=20)
        decided = cc.classify([decision(proposal, amended=True, exact_payload=None, amount_usd=12.5,
                                        amended_sha256=his_digest(12.5, None))], [proposal])
        self.assertEqual(decided['approved'][proposal['proposal_id']]['amount_usd'], 12.5)
        self.assertIn('12.5 USD', decided['instructions'][0]['line'])

    def test_a_digest_mismatch_or_a_missing_digest_counts_for_nothing(self):
        proposal = post()
        wrong = decision(proposal, amended=True, exact_payload='His words.', amount_usd=None,
                         amended_sha256=his_digest(None, 'Other words.'))
        missing = {k: v for k, v in wrong.items() if k != 'amended_sha256'}
        for value in (wrong, missing):
            decided = cc.classify([value], [proposal])
            self.assertEqual(decided['amended_unverified'], [proposal['proposal_id']])
            for key in ('approved_current', 'approved_amended', 'approved_changed', 'instructions'):
                self.assertEqual(decided[key], [])
            self.assertEqual(decided['approved'], {})

    def test_an_unamended_yes_binds_its_payload_digest(self):
        proposal = post()
        same = cc.classify([decision(proposal)], [proposal])
        self.assertEqual(same['approved_current'], [proposal['proposal_id']])
        self.assertEqual(same['approved'][proposal['proposal_id']]['exact_payload'], 'Engine words.')
        changed = cc.classify([decision(proposal, payload_sha256='f' * 64)], [proposal])
        self.assertEqual((changed['approved_changed'], changed['approved'], changed['instructions']),
                         ([proposal['proposal_id']], {}, []))


class HandcraftedTests(unittest.TestCase):
    def test_an_approved_post_is_an_instruction_for_krish_never_an_action(self):
        proposal = post()
        decided = cc.classify([decision(proposal)], [proposal])
        instruction = decided['instructions'][0]
        self.assertEqual((instruction['proposal_id'], instruction['by'], instruction['sha256']),
                         (proposal['proposal_id'], 'krish', proposal['payload_sha256']))
        self.assertIn('post it yourself on youtube', instruction['line'])
        self.assertIn('does not post, send or spend', instruction['line'])

    def test_a_ruling_yes_is_no_instruction(self):
        report = sample_report()
        d7 = next(p for p in report['proposals'] if p['proposal_id'] == 'fulltime:ruling:D7')
        decided = cc.classify([decision(d7)], report['proposals'])
        self.assertEqual((decided['approved_current'], decided['instructions']), (['fulltime:ruling:D7'], []))

    def test_instructions_and_answers_are_recorded_once_each(self):
        proposal = post()
        decided = cc.classify([decision(proposal)], [proposal])
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(cc.record_instructions(root, decided['instructions'] * 2, '2026-10-27T08:00:00Z'), 1)
            self.assertEqual(cc.record_instructions(root, decided['instructions'], '2026-10-28T08:00:00Z'), 0)
            self.assertEqual(cc.record_answers(root, decided, '2026-10-27T08:00:00Z'), 1)
            self.assertEqual(cc.record_answers(root, decided, '2026-10-28T08:00:00Z'), 0)
            rows = (Path(root) / 'control-center' / 'instructions.jsonl').read_text(encoding='utf-8').splitlines()
        self.assertEqual(len(rows), 1)
        self.assertEqual(json.loads(rows[0])['recorded_at'], '2026-10-27T08:00:00Z')


class VersionStandIn(StandIn):
    def __init__(self):
        super().__init__()
        self.directive_version = '1.0.0'
        self.decisions_version = None

    def _directive(self):
        payload = super()._directive()
        payload['directive']['schema_version'] = self.directive_version
        return payload

    def get_decisions(self, h, route, query, body):
        out = {'ok': True, 'decisions': self.decisions}
        if self.decisions_version:
            out['schema_version'] = self.decisions_version
        return h._send(200, out)


class VersionRefusalTests(unittest.TestCase):
    def setUp(self):
        self.server = VersionStandIn()
        self.addCleanup(self.server.close)
        self.report = sample_report()

    def loop(self):
        client = cc.Client(self.server.url, TOKEN, loopback_for_tests=True)
        with contextlib.redirect_stdout(io.StringIO()):
            return cc.execute(client, 'morning', self.report['run_id'], lambda d: (self.report, {}),
                              '2026-10-18T00:00:00Z')

    def test_any_1x_is_taken_and_another_major_is_refused(self):
        for value in (None, '1.0.0', '1.1.0', '1.20.0'):
            self.assertTrue(cc.version_supported(value), value)
        for value in ('2.0.0', '0.9.0', '10.0.0', '1.1', 'one', 1):
            self.assertFalse(cc.version_supported(value), value)

    def test_a_2x_directive_is_refused_with_a_code_and_nothing_is_reported(self):
        self.server.directive_version = '2.0.0'
        summary = self.loop()
        self.assertEqual((summary['status'], summary['phase'], summary['error_code']),
                         ('failed', 'directive', 'protocol_version_unsupported'))
        self.assertEqual(self.server.reports, {})

    def test_a_later_1x_directive_is_taken(self):
        self.server.directive_version = '1.38.0'
        self.assertEqual(self.loop()['status'], 'succeeded')

    def test_a_2x_decision_counts_for_nothing_and_a_2x_answer_is_refused(self):
        d7 = next(p for p in self.report['proposals'] if p['proposal_id'] == 'fulltime:ruling:D7')
        self.server.decisions = [{**decision(d7), 'schema_version': '2.0.0'}]
        decided = self.loop()['decisions']
        self.assertEqual(decided['refused'], [{'proposal_id': 'fulltime:ruling:D7',
                                               'code': 'protocol_version_unsupported'}])
        self.assertEqual(decided['approved'], {})
        self.server.decisions_version = '2.0.0'
        self.report = reporting.seal({**{k: v for k, v in self.report.items() if k != 'payload_sha256'},
                                      'run_id': 'fulltime:2026-10-20:daily'})
        summary = self.loop()
        self.assertEqual((summary['status'], summary['phase'], summary['error_code']),
                         ('failed', 'decisions', 'protocol_version_unsupported'))


if __name__ == '__main__':
    unittest.main()
