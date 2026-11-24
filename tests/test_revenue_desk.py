"""The revenue desk adapter (Ruling, Krish, 2026-11-24): config/revenue-desk.json parses and names real sources.

Full Time is measure first: no counted step, so the one output is the reading plan for attributed_new_completers.
No network and no figures.
"""
import json
import os
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / 'config' / 'revenue-desk.json'


def load():
    return json.loads(ADAPTER.read_text(encoding='utf-8'))


def source_errors(cfg, root=ROOT):
    """Every path the adapter names exists, and every named function is defined there."""
    errors = []
    reads = [r for step in cfg['money_path'] for r in step['read']]
    paths = [r['path'] for r in reads] + list(cfg['reading_plan']['spec']) + [cfg['north_star']['doc']]
    paths += [ref.split(' ')[0] for ref in cfg['reading_plan']['scored_by']]
    for path in paths:
        if not (root / path).exists():
            errors.append('missing ' + path)
    for ref in reads + [{'path': p, 'function': f} for p, f in (s.split(' ') for s in cfg['reading_plan']['scored_by'])]:
        if 'function' in ref and (root / ref['path']).exists():
            text = (root / ref['path']).read_text(encoding='utf-8')
            if not re.search(r'^def ' + re.escape(ref['function']) + r'\(', text, re.M):
                errors.append('undefined ' + ref['path'] + ' ' + ref['function'])
    return errors


class RevenueDeskAdapterTest(unittest.TestCase):
    def test_the_adapter_parses_and_is_measure_first(self):
        cfg = load()
        self.assertEqual(cfg['schema'], 'revenue-desk-adapter/1')
        self.assertEqual(cfg['method']['name'], 'revenue-desk')
        self.assertEqual(cfg['venture'], 'fulltime')
        self.assertEqual(cfg['stage'], 'measure first')
        self.assertEqual(cfg['spend_authority'], 'none')
        self.assertTrue(cfg['sheets'].startswith('local/'))
        for step in cfg['money_path']:
            self.assertEqual(step['stage'], 'measure_first', step['step'])

    def test_the_one_output_is_the_reading_plan_for_the_north_star(self):
        cfg = load()
        self.assertEqual(cfg['north_star']['metric'], 'attributed_new_completers')
        self.assertEqual(cfg['reading_plan']['metric'], 'attributed_new_completers')
        self.assertIn('attributed_new_completers', (ROOT / 'MEASUREMENT.md').read_text(encoding='utf-8'))
        for command in cfg['reading_plan']['import']:
            self.assertTrue(command.startswith('python3 growth.py '), command)

    def test_every_named_source_exists(self):
        self.assertEqual(source_errors(load()), [])

    def test_bands_are_unset_assumptions(self):
        bands = load()['bands']
        self.assertEqual(bands['status'], 'assumption')
        self.assertFalse(bands['binding'])
        self.assertEqual(bands['per_step'], {})

    def test_no_em_dash_exclamation_or_figure_and_agents_points_to_it(self):
        text = ADAPTER.read_text(encoding='utf-8')
        for bad in (chr(0x2014), '!', '$', chr(0xa3)):
            self.assertNotIn(bad, text)
        agents = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
        self.assertIn('## Revenue desk', agents)
        self.assertIn('config/revenue-desk.json', agents)


if __name__ == '__main__':
    unittest.main()
