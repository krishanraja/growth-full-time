"""divergent-thinker and humour-engine through Control Center (engine/divergent.py, engine/humour.py).

Stand-in clients only: nothing here reaches the network, and nothing posts, sends or spends."""
import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from engine import divergent, humour, insight_sheet
from engine.control_center import Client, ControlCenterError


class FakeCC:
    def __init__(self, features=None, error=None, answer=None, held=False, cap_error=None):
        self.features = features if features is not None else {'divergent': True, 'humour': True}
        self.error, self.answer, self.held, self.cap_error = error, answer, held, cap_error
        self.calls = []

    def capabilities(self):
        self.calls.append('capabilities')
        if self.error:
            raise self.error
        return {'ok': True, 'features': self.features}

    def directive(self):
        self.calls.append('directive')
        return {'ok': True, 'directive': {'engine_state': {'held': self.held}, 'held': self.held}}

    def divergent(self, body):
        self.calls.append(('divergent', body))
        if self.cap_error:
            raise self.cap_error
        return self.answer or {'ok': True, 'results': []}

    def humour(self, body):
        self.calls.append(('humour', body))
        return {'ok': True, 'payload': {}}


def creative(caption, at='2026-11-23T09:00:00+00:00', status='published'):
    return {'status': status, 'publication': {'url': 'https://example.invalid/p', 'recorded_at': at},
            'versions': [{'item': {'caption': caption + ' https://fulltime.fm/x'}}]}


CREATIVES = {'c1': creative('The Doomer saw it coming.'), 'c2': creative('Stats says no.', at='2026-11-01T09:00:00+00:00'),
             'c3': creative('Held one.', status='held')}
ITEMS = [{'item_id': 'a', 'caption': 'The Doomer saw it coming again.'}, {'item_id': 'b', 'text': 'A fresh take.'}]


class Served(unittest.TestCase):
    def test_dormant_until_control_center_serves_it(self):
        cc = FakeCC(features={})
        self.assertFalse(divergent.served(cc))
        out = divergent.guard_copy(cc, ITEMS, ['x'])
        self.assertEqual(out['status'], 'not_served')
        self.assertFalse([c for c in cc.calls if isinstance(c, tuple)])

    def test_an_unreadable_capabilities_is_not_served(self):
        self.assertFalse(divergent.served(FakeCC(error=ControlCenterError('network_error'))))
        self.assertFalse(divergent.served(None))


class Copy(unittest.TestCase):
    def test_published_captions_newest_first_links_removed_held_left_out(self):
        self.assertEqual(divergent.published_captions(CREATIVES), ['The Doomer saw it coming.', 'Stats says no.'])
        self.assertEqual(divergent.published_captions(CREATIVES, '2026-11-20'), ['The Doomer saw it coming.'])

    def test_the_batch_scores_against_published_captions_with_no_model_call(self):
        cc = FakeCC(answer={'ok': True, 'results': [{'status': 'rejected_archive'}, {'status': 'accepted'}]})
        lines = divergent.batch_lines(cc, ITEMS, CREATIVES, '2026-11-20')
        score = next(body for kind, body in (c for c in cc.calls if isinstance(c, tuple)) if body['op'] == 'score')
        self.assertEqual(score['obvious'], ['The Doomer saw it coming.', 'Stats says no.'])
        self.assertEqual(score['namespace'], 'growth-fulltime:copy')
        self.assertNotIn('judge', score)   # the judge spends model calls; the batch never asks it
        self.assertIn('1 flagged, none dropped', lines[0])
        self.assertTrue(any('recorded 1 published captions' in line for line in lines))

    def test_with_nothing_published_there_is_no_score(self):
        cc = FakeCC()
        out = divergent.guard_copy(cc, ITEMS, [])
        self.assertEqual(out['status'], 'skipped')
        self.assertFalse([c for c in cc.calls if isinstance(c, tuple)])

    def test_a_cap_or_refusal_is_a_quiet_line_never_retried(self):
        cc = FakeCC(cap_error=ControlCenterError('rate_limited', 429, 'daily_quick_cap_reached'))
        out = divergent.guard_copy(cc, ITEMS, ['x'])
        self.assertEqual(out['status'], 'unavailable')
        self.assertIn('daily_quick_cap_reached', out['note'])
        self.assertEqual(len([c for c in cc.calls if isinstance(c, tuple)]), 1)


class AtWill(unittest.TestCase):
    def test_bodies_keep_the_namespace_and_need_their_inputs(self):
        self.assertEqual(divergent.at_will_body('record', items=['a'], lane='ideas')['namespace'], 'growth-fulltime:ideas')
        for op, kwargs in (('map', {}), ('score', {'problem': 'p'}), ('challenge', {'problem': 'p'}), ('record', {})):
            with self.assertRaises(ValueError):
                divergent.at_will_body(op, **kwargs)
        with self.assertRaises(ValueError):
            divergent.at_will_body('map', problem='p', lane='Bad Lane')

    @mock.patch('engine.activation.local_state', return_value='active')
    def test_a_generating_op_refuses_while_held_and_spends_nothing(self, _active):
        cc = FakeCC(held=True)
        code, answer, reason = divergent.at_will(cc, divergent.at_will_body('provoke', problem='p'))
        self.assertEqual((code, answer), (divergent.EXIT_UNAVAILABLE, None))
        self.assertIn('held', reason)
        self.assertFalse([c for c in cc.calls if isinstance(c, tuple)])

    @mock.patch('engine.activation.local_state', return_value='active')
    def test_exit_codes(self, _active):
        flagged = FakeCC(answer={'ok': True, 'results': [{'status': 'rejected_gravity'}]})
        self.assertEqual(divergent.at_will(flagged, divergent.at_will_body('score', problem='p', ideas=['x']))[0], 1)
        self.assertEqual(divergent.at_will(FakeCC(), divergent.at_will_body('score', problem='p', ideas=['x']))[0], 0)
        self.assertEqual(divergent.at_will(FakeCC(features={}), divergent.at_will_body('map', problem='p'))[0], 2)
        capped = FakeCC(cap_error=ControlCenterError('rate_limited', 429, 'daily_diverge_cap_reached'))
        code, _, reason = divergent.at_will(capped, divergent.at_will_body('diverge', problem='p'))
        self.assertEqual(code, 2)
        self.assertIn('daily_diverge_cap_reached', reason)

    def test_command_with_no_token_is_unavailable(self):
        with tempfile.TemporaryDirectory() as d, contextlib.redirect_stderr(io.StringIO()):
            ideas = Path(d) / 'ideas.txt'
            ideas.write_text('one\ntwo\n', encoding='utf-8')

            def no_client():
                raise ControlCenterError('missing_token')
            self.assertEqual(divergent.command(['score', '--problem', 'p', '--ideas-file', str(ideas)], no_client), 2)


def analysis(reading='supported', target='behaviour', deps=0, attempt='supported_inference', missing=()):
    return {'comic_reading': reading, 'humour_attempt': {'status': attempt} if attempt else None,
            'interpretations': [{'is_main': True, 'supported_reading': 'comic' if reading == 'supported' else None,
                                 'labels_by_axis': {'mechanism': ['incongruity']},
                                 'target_and_subject': {'target': target}}],
            'context_dependencies': [{'source_kind': 'topical', 'required': True}] * deps,
            'missing_context': list(missing)}


class Humour(unittest.TestCase):
    def test_a_joke_at_a_person_is_held_and_one_at_the_football_passes(self):
        self.assertTrue(humour.findings(analysis(target='other_person'))[0][0].startswith('at_person'))
        self.assertEqual(humour.findings(analysis(target='situation'))[0], [])
        self.assertEqual(humour.findings(analysis(target='institution'))[0], [])

    def test_a_joke_that_needs_explaining_is_held_and_a_forced_one_is_a_note(self):
        self.assertTrue(humour.findings(analysis(deps=2))[0])
        self.assertTrue(humour.findings(analysis(missing=['who scored']))[0])
        rules, notes, _ = humour.findings(analysis(reading='not_supported'))
        self.assertEqual(rules, [])
        self.assertTrue(notes[0].startswith('forced'))

    def test_unavailable_is_never_a_pass(self):
        self.assertEqual(humour.consult(['A line.'], read=None)['status'], 'unavailable')

        def boom(_):
            raise RuntimeError('provider down')
        self.assertEqual(humour.consult(['A line.'], read=boom)['status'], 'unavailable')
        self.assertEqual(humour.consult(['A line.'], read=lambda _: {'comic_reading': None})['status'], 'unavailable')
        self.assertEqual(humour.consult(['A line.'], read=lambda _: analysis())['status'], 'pass')

    def test_the_request_is_one_model_call_through_control_center(self):
        req = humour.request(['One.', 'Two.'], 'caption')
        self.assertEqual(req['budget']['max_model_calls'], 1)
        self.assertEqual(req['provider_policy']['allowed_provider_ids'], ['controlcenter'])
        self.assertEqual(len(req['segments']), 2)

    def test_the_transport_keeps_control_centers_refusal_code(self):
        class Capped(FakeCC):
            def humour(self, body):
                raise ControlCenterError('rate_limited', 429, 'daily_humour_cap_reached')
        self.assertEqual(humour.transport_for(Capped())('ignored', {}), (429, {'ok': False, 'error': 'daily_humour_cap_reached'}))

    def test_doctor_needs_the_token_the_package_and_the_route(self):
        self.assertFalse(humour.doctor(None, package=True)[0])
        self.assertFalse(humour.doctor(FakeCC(features={}), package=True)[0])
        self.assertTrue(humour.doctor(FakeCC(), package=True)[0])


class ClientRoutes(unittest.TestCase):
    def test_a_refusal_keeps_control_centers_code(self):
        client = Client('https://controlcenter.example', 'x' * 40)
        client._call = lambda *a, **k: (429, {'ok': False, 'error': 'daily_diverge_cap_reached'})
        with self.assertRaises(ControlCenterError) as caught:
            client.divergent({'op': 'diverge'})
        self.assertEqual((caught.exception.code, caught.exception.server_code), ('rate_limited', 'daily_diverge_cap_reached'))
        client._call = lambda *a, **k: (200, {'ok': True, 'features': {'divergent': True}})
        self.assertTrue(client.capabilities()['features']['divergent'])


class Adapter(unittest.TestCase):
    def test_the_insight_adapter_names_both_routes(self):
        adapter = insight_sheet.load_adapter()
        self.assertEqual(insight_sheet.adapter_errors(adapter), [])
        self.assertEqual(adapter['divergent']['scheduled_run'], 'score-and-record')
        self.assertTrue(adapter['humour']['allowed'])
        bad = json.loads(json.dumps(adapter))
        bad['divergent']['scheduled_run'] = 'diverge'
        self.assertTrue(insight_sheet.adapter_errors(bad))


if __name__ == '__main__':
    unittest.main()
