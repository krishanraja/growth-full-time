"""The humour engine, on call: does a joke in Full Time's public copy land, how, and at whose expense.

humour-engine (krishanraja/humour-engine) is the fleet's one definition and understanding of humour; each
engine keeps its own stylistic preferences. Full Time's are the AI Pundits' own (krishanraja/full-time and
the creative system own their voice and delivery), so this file never writes or rewrites a joke. It reads
the engine's analysis of a caption and turns it into three rules this repository already holds:

  at_person          the joke is at a person (a player, a manager, a rival fan), not at the football. COPY.md rule 6: nothing leans on rivalry abuse.
  needs_explaining   the joke leans on more than one outside reference, or on context the reader is not
                     given, so a fan scrolling past cannot send it to a mate (the North Star counts shares).
  forced             a note, never a rule: a line that tries to be funny and does not land.

It runs through this engine's own Control Center client and bearer (POST
/api/growth/engines/fulltime/humour, capped by Control Center at 200 calls a day) and needs the humour-engine
package for the prompt and the validators (`pip install -r requirements-humour.txt && pip install --no-deps
-r requirements-humour-engine.txt`). Without either it says unavailable, and unavailable is never a pass.
It is a check a session runs on a caption before Krish sees it. It approves, sends and posts nothing.
"""

import hashlib
import os

from .control_center import ControlCenterError
from .reporting import SLUG

SURFACES = {
    'caption': "Format: the caption under one of Full Time's AI Pundit posts or clips",
    'onscreen': 'Format: words on screen in a short vertical clip or a card',
    'reply': "Format: a public reply from Full Time's account under another account's post",
    'line': 'Format: a single line of social copy',
}
AUDIENCE = 'Football fans on social media who might listen to an AI Pundit talk about the match they just watched'
EXIT = {'pass': 0, 'flagged': 1, 'unavailable': 2}
AT_PEOPLE = ('other_person',)  # humour-engine's target axis; a club, the league or the game is not a person


def words_sha(lines):
    return hashlib.sha256('\n'.join(lines).encode('utf-8')).hexdigest()[:16]


def request(lines, surface='line', context=(), request_id='fulltime:check'):
    """The humour-engine AnalysisRequest for these lines: one segment a line, one model call."""
    segs = [{'segment_id': 'l%d' % n, 'text': w, 'sequence': n} for n, w in enumerate(lines, 1)]
    facts = [SURFACES.get(surface, SURFACES['line'])] + [str(c)[:500] for c in context][:5]
    return {
        'request_id': request_id,
        'focus_segment_ids': [s['segment_id'] for s in segs],
        'segments': segs,
        'context': {'provided_facts': facts, 'audience_description': AUDIENCE},
        'tasks': ['comprehension'],
        'provider_policy': {'allowed_provider_ids': ['controlcenter'], 'allow_external_inference': True},
        'budget': {'max_model_calls': 1, 'max_input_tokens': 9000, 'max_output_tokens': 2000},
    }


def transport_for(cc):
    """Adapt this engine's Client to humour-engine's ControlCenterProvider transport: (url, body) -> (status, json).
    The client's own origin lock, bearer and error codes apply; the provider's URL is ignored."""
    def transport(_url, body):
        try:
            return 200, cc.humour(body)
        except ControlCenterError as e:
            return e.status or 503, {'ok': False, 'error': e.server_code or e.code}
    return transport


def reader(cc):
    """A function request -> analysis dict, or None when the package is not installed or there is no client."""
    if cc is None or not hasattr(cc, 'humour'):
        return None
    try:
        import json
        from humour_engine.analysis.core import EngineDeps, analyse
        from humour_engine.contracts.analysis import AnalysisRequest
        from humour_engine.models.providers import ControlCenterProvider
    except ImportError:
        return None
    os.environ.setdefault(ControlCenterProvider.ENGINE_ENV, SLUG)
    deps = EngineDeps(providers={'controlcenter': ControlCenterProvider(transport=transport_for(cc))},
                      max_calls_per_request=1)

    def read(req):
        return json.loads(analyse(AnalysisRequest.model_validate(req), deps).model_dump_json())
    return read


def _main(result):
    main = [i for i in result.get('interpretations', []) if i.get('supported_reading')]
    return next((i for i in main if i.get('is_main')), main[0]) if main else None


def findings(result):
    """(rules broken, notes, labels) from one analysis. Rules hold a caption; notes inform it."""
    rules, notes, labels = [], [], {}
    reading = result.get('comic_reading')
    i = _main(result)
    if i:
        labels = {k: v for k, v in (i.get('labels_by_axis') or {}).items() if v}
        target = (i.get('target_and_subject') or {}).get('target')
        if target:
            labels['target'] = [target]
    attempted = (result.get('humour_attempt') or {}).get('status') in ('reported', 'supported_inference')
    if reading == 'supported':
        if (labels.get('target') or [None])[0] in AT_PEOPLE:
            rules.append('at_person: the joke is at a person, not the football; nothing '
                         'leans on rivalry abuse (COPY.md rule 6)')
        jumps = [d for d in result.get('context_dependencies', [])
                 if d.get('required') and d.get('source_kind') in ('cultural', 'topical')]
        if len(jumps) > 1 or result.get('missing_context'):
            rules.append('needs_explaining: it leans on more than one outside reference, so a fan cannot send it '
                         'to a mate without explaining it')
    elif reading == 'insufficient_context' and attempted:
        rules.append('needs_explaining: the engine cannot read the joke without context the reader is not given')
    elif reading in ('ambiguous', 'not_supported') and attempted:
        notes.append('forced: it reads as an attempt at a joke that does not land; cut the joke or rewrite it')
    return rules, notes, labels


def consult(lines, surface='line', context=(), read=None):
    """One read. status: pass, flagged or unavailable. Unavailable is never a pass."""
    lines = [w.strip() for w in lines if w and w.strip()]
    out = {'surface': surface, 'lines': len(lines), 'words_sha': words_sha(lines)}
    if read is None:
        out.update(status='unavailable', reason='humour engine not reachable: run `python3 growth.py humour doctor`')
        return out
    try:
        result = read(request(lines, surface, context))
    except Exception as e:  # noqa: BLE001  a provider or contract failure is never a pass
        out.update(status='unavailable', reason='humour engine failed: ' + type(e).__name__)
        return out
    reading = result.get('comic_reading')
    if reading is None:
        codes = [e.get('code') for e in result.get('errors', []) if isinstance(e, dict)]
        out.update(status='unavailable', reason='no reading: ' + (', '.join(c for c in codes if c) or 'the engine abstained'))
        return out
    rules, notes, labels = findings(result)
    out.update(reading=reading, rules=rules, notes=notes, labels=labels,
               status='flagged' if rules or notes else 'pass')
    return out


def render(o):
    rows = ['%s  (%s, %d line(s), %s)' % (o['status'].upper(), o['surface'], o['lines'], o['words_sha'])]
    if o.get('reason'):
        rows.append('  ' + o['reason'])
    if o.get('reading'):
        rows.append('  reading: ' + o['reading'])
    for k in ('mechanism', 'rhetorical_mode', 'target'):
        if o.get('labels', {}).get(k):
            rows.append('  %s: %s' % (k, ', '.join(o['labels'][k])))
    rows += ['  - ' + r for r in o.get('rules', [])] + ['  - note: ' + n for n in o.get('notes', [])]
    return '\n'.join(rows)


def doctor(cc, package=None):
    """(ok, lines). Checks the client, the package and that Control Center serves the route. No model call;
    never prints the token."""
    lines, ok = [], True
    if cc is None:
        ok = False
        lines.append('token: NOT READY. No engine token here; the GitHub runner and the workspace have it')
    else:
        lines.append('token: the engine token is set')
    if package is None:
        try:
            import humour_engine  # noqa: F401
            package = True
        except ImportError:
            package = False
    if package:
        lines.append('package: humour-engine installed')
    else:
        ok = False
        lines.append('package: NOT INSTALLED. pip install -r requirements-humour.txt && '
                     'pip install --no-deps -r requirements-humour-engine.txt')
    if cc is not None:
        try:
            features = (cc.capabilities() or {}).get('features') or {}
            if features.get('humour'):
                lines.append('route: Control Center serves the humour route to this engine')
            else:
                ok = False
                lines.append('route: NOT SERVED. Control Center answered, but features.humour is off for this engine')
        except ControlCenterError as e:
            ok = False
            lines.append('route: UNREACHABLE (' + e.code + ')')
    lines.append('ready: the humour engine can be consulted' if ok
                 else 'ready: NO. `humour check` will say unavailable, never pass')
    return ok, lines


def command(argv, client_factory):
    """growth.py humour check|doctor. Exit 0 pass, 1 flagged, 2 unavailable."""
    import argparse
    import json
    p = argparse.ArgumentParser(prog='growth.py humour', description=__doc__.split('\n')[0])
    sub = p.add_subparsers(dest='action', required=True)
    x = sub.add_parser('check')
    x.add_argument('lines', nargs='*'); x.add_argument('--file'); x.add_argument('--json', action='store_true')
    x.add_argument('--surface', choices=sorted(SURFACES), default='caption')
    x.add_argument('--context', action='append', default=[])
    sub.add_parser('doctor')
    a = p.parse_args(argv)

    def client():
        try:
            return client_factory()
        except ControlCenterError:
            return None
    if a.action == 'doctor':
        ok, rows = doctor(client())
        print('\n'.join(rows))
        return 0 if ok else 2
    lines = list(a.lines)
    if a.file:
        with open(a.file, encoding='utf-8-sig') as f:
            lines += [line.strip() for line in f if line.strip()]
    if not lines:
        p.error('give the line(s) as arguments or with --file')
    o = consult(lines, a.surface, a.context, reader(client()))
    print(json.dumps(o, ensure_ascii=False, indent=2) if a.json else render(o))
    return EXIT[o['status']]
