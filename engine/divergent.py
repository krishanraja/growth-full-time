"""divergent-thinker, on call: the fleet's divergent thinking engine, through Control Center.

It measures how far a line sits from the obvious one, and on request proposes ideas outside the consensus.
It never sends, posts, publishes or spends: what it gives back is a reading for this engine, and an idea
reaches Krish only as this engine's own proposal behind the strategy wall. It runs on this engine's own
client and bearer (POST /api/growth/engines/fulltime/divergent) and is dormant until Control Center serves
it: every use first reads capabilities, and with `features.divergent` not true it makes no call and says
"not served", never an error.

Cheapest first. Three uses:

  copy       The morning batch scores the captions it prepared against the captions already published
             (`obvious`), namespace growth-fulltime:copy. Zero model calls: with nothing published held
             there is no score, never a paid consensus. A caption that sits on the obvious one
             (rejected_gravity) or repeats one already out (rejected_archive) is flagged in the report,
             never dropped or rewritten.
  record     The same batch records the captions published in the last three days to that namespace, so
             the next batch is scored against them. Zero model calls.
  at will    A session runs `python3 growth.py divergent <op>`. score and record are free; map, provoke,
             challenge and diverge spend model calls on Control Center's key, so they refuse while the
             engine is held and Control Center caps them per engine per day (one diverge, twenty quick
             calls, five dollars). A cap answer (429) is final: nothing here retries or routes around it.
             The paid moves are for U4 and U5, a weekly idea that keeps coming back the same, or an angle
             about to be committed.

A refusal (400, 403, 404, 409 held, 429 daily cap, 503) is a quiet line, never a failed run and never retried.
"""
import json
import re
from pathlib import Path

from .control_center import ControlCenterError

FEATURE = 'divergent'
NAMESPACE = 'growth-fulltime'
COPY = NAMESPACE + ':copy'
MAX_IDEAS, MAX_OBVIOUS, MAX_RECORD = 100, 30, 200
RECORD_DAYS = 3  # the morning batch runs daily; three days of published captions covers a missed run
FLAGGED = ('rejected_gravity', 'rejected_archive')
NOT_SERVED = 'divergent-thinker: not served (Control Center has not switched features.divergent on); no call made'
COPY_PROBLEM = ("An AI Pundit's caption that makes a football fan stop scrolling, listen, and send the show to a mate "
                '(new listeners a week who arrived through a shared link or clip)')
# Words divergent-thinker's gate rejects in an idea: the copy floor's banned register (COPY.md, rules 6 and 7).
BANNED_WORDS = ('betting', 'tipster', 'accumulator', 'guaranteed', 'game-changer', 'revolutionary',
                'unlock', 'leverage', 'seamless')

OPS = ('map', 'provoke', 'challenge', 'diverge', 'score', 'record')
GENERATING = ('map', 'provoke', 'challenge', 'diverge')
COST = {'map': '1 model call', 'provoke': '2 model calls, about $0.15', 'challenge': '3 model calls',
        'diverge': 'about 25 model calls and about $1.30, one a day', 'score': 'no model call with --obvious-file',
        'record': 'no model call'}
LANE = re.compile(r'^[a-z0-9][a-z0-9-]{0,39}$')  # Control Center's namespace rule
EXIT_OK, EXIT_FLAGGED, EXIT_UNAVAILABLE = 0, 1, 2


def served(client):
    """True only when Control Center's capabilities say features.divergent is true. Never raises."""
    if client is None or not hasattr(client, 'divergent'):
        return False
    try:
        features = (client.capabilities() or {}).get('features')
    except ControlCenterError:
        return False
    return isinstance(features, dict) and features.get(FEATURE) is True


def refusal(error):
    """The quiet line for a refused or failed call: Control Center's code when it gave one, else ours."""
    code = getattr(error, 'server_code', None) or getattr(error, 'code', None) or type(error).__name__
    return 'divergent-thinker: not consulted (' + str(code) + '); nothing was retried'


def _words(value):
    return ' '.join(str(value or '').split())


URL = re.compile(r'https?://\S+', re.I)


def caption_of(item):
    """The public words of a pack item or a creative version: its caption, else its text, links removed."""
    if not isinstance(item, dict):
        return ''
    words = item.get('caption') if isinstance(item.get('caption'), str) else item.get('text')
    return _words(URL.sub(' ', words if isinstance(words, str) else ''))


def published_captions(creatives, since_date=None):
    """The latest caption of each published creative (recorded on or after since_date), newest first, each once."""
    rows = []
    for creative in (creatives or {}).values():
        if not isinstance(creative, dict) or creative.get('status') != 'published' or not creative.get('versions'):
            continue
        at = str((creative.get('publication') or {}).get('recorded_at') or '')
        if since_date and at[:10] < since_date:
            continue
        words = caption_of((creative['versions'][-1] or {}).get('item'))
        if words:
            rows.append((at, words))
    seen, out = set(), []
    for _, words in sorted(rows, reverse=True):
        if words not in seen:
            seen.add(words)
            out.append(words)
    return out


def guard_copy(client, items, published):
    """{status, note, flags}: the prepared captions scored against the published ones. Zero model calls."""
    drafts = [(str(item.get('item_id') or item.get('creative_id') or n), caption_of(item))
              for n, item in enumerate(items or [], 1) if isinstance(item, dict)]
    drafts = [(where, words) for where, words in drafts if words][:MAX_IDEAS]
    obvious = [w for w in (published or []) if w][:MAX_OBVIOUS]
    if not drafts:
        return {'status': 'skipped', 'note': 'divergent-thinker: no prepared caption to score', 'flags': []}
    if not served(client):
        return {'status': 'not_served', 'note': NOT_SERVED, 'flags': []}
    if not obvious:
        return {'status': 'skipped', 'note': 'divergent-thinker: no published caption held, so the batch was not '
                                             'scored (without one a score would spend model calls)', 'flags': []}
    body = {'op': 'score', 'problem': COPY_PROBLEM, 'ideas': [w for _, w in drafts], 'obvious': obvious,
            'bannedWords': list(BANNED_WORDS), 'namespace': COPY}
    try:
        answer = client.divergent(body)
    except ControlCenterError as error:
        return {'status': 'unavailable', 'note': refusal(error), 'flags': []}
    results = answer.get('results') if isinstance(answer.get('results'), list) else []
    flags = [{'where': where, 'status': r.get('status'),
              'why': 'sits on the obvious caption' if r.get('status') == 'rejected_gravity'
              else 'repeats a caption already out'}
             for (where, _), r in zip(drafts, results) if isinstance(r, dict) and r.get('status') in FLAGGED]
    note = ('divergent-thinker scored ' + str(len(drafts)) + ' prepared captions against ' + str(len(obvious))
            + ' published ones (no model call): ' + str(len(flags)) + ' flagged, none dropped'
            + ('; ' + ', '.join(f['where'] + ' ' + f['why'] for f in flags) if flags else ''))
    return {'status': 'scored', 'note': note[:500], 'flags': flags}


def record_live(client, published):
    """One record call with the recently published captions, when served. A line with counts only, never words."""
    items = [w for w in (published or []) if w][:MAX_RECORD]
    if not items:
        return None
    if not served(client):
        return NOT_SERVED
    try:
        client.divergent({'op': 'record', 'items': items, 'namespace': COPY, 'label': 'published captions'})
    except ControlCenterError as error:
        return refusal(error)
    return 'divergent-thinker: recorded ' + str(len(items)) + ' published captions to ' + COPY + ' (no model call)'


def batch_lines(client, items, creatives, since_date):
    """The morning batch's two free uses, as report activity lines. Never raises for the route."""
    lines = [guard_copy(client, items, published_captions(creatives))['note']]
    recorded = record_live(client, published_captions(creatives, since_date))
    if recorded and recorded != lines[0]:
        lines.append(recorded)
    return lines


# At will: any session in this repository, by hand -----------------------------

def items_of(path):
    """A JSON list of strings, or one item a line. Blank lines and blank items are dropped."""
    text = Path(path).read_text(encoding='utf-8-sig')
    try:
        value = json.loads(text)
    except ValueError:
        value = None
    rows = value if isinstance(value, list) else text.splitlines()
    return [w for w in (_words(x) for x in rows) if w]


def at_will_body(op, problem=None, context=None, idea=None, ideas=(), obvious=(), items=(), cliches=(),
                 count=None, target=None, temperament=None, lane=None, judge=False, label=None):
    """The exact body Control Center's route takes for one at-will op. Raises ValueError on a missing input."""
    if op not in OPS:
        raise ValueError('op must be one of ' + ', '.join(OPS))
    if lane is not None and not LANE.match(lane):
        raise ValueError('--lane is lower case letters, digits and - (at most 40)')
    namespace = NAMESPACE + (':' + lane if lane else '')
    if op == 'record':
        if not items:
            raise ValueError('record needs --items-file with at least one item')
        body = {'op': op, 'items': list(items)[:MAX_RECORD], 'namespace': namespace}
        if label:
            body['label'] = label
        return body
    if not (problem or '').strip():
        raise ValueError(op + ' needs --problem')
    body = {'op': op, 'problem': _words(problem)}
    if op == 'score':
        if not ideas:
            raise ValueError('score needs --ideas-file with at least one idea')
        body.update(ideas=list(ideas)[:MAX_IDEAS], bannedWords=list(BANNED_WORDS), namespace=namespace)
        if obvious:
            body['obvious'] = list(obvious)[:MAX_OBVIOUS]
        if judge:
            body['judge'] = True
        return body
    if context:
        body['context'] = _words(context)
    if op == 'map':
        return body
    if op == 'challenge':
        if not (idea or '').strip():
            raise ValueError('challenge needs --idea')
        body['idea'] = _words(idea)
        return body
    body.update(bannedWords=list(BANNED_WORDS), namespace=namespace)
    if cliches:
        body['cliches'] = [_words(c) for c in cliches if c.strip()]
    for key, value in (('count', count), ('target', target), ('temperament', temperament)):
        if value is not None:
            body[key] = value
    return body


def flagged(answer):
    """The score results divergent-thinker rejected (any rejected_* status)."""
    results = answer.get('results') if isinstance(answer.get('results'), list) else []
    return [r for r in results if isinstance(r, dict) and str(r.get('status') or '').startswith('rejected')]


def at_will(client, body):
    """(exit code, answer or None, reason or None). One call at most, never retried, never written to his list.

    Not served, unreachable, a refusal, or a held engine for a generating op is exit 2 with its reason; a score
    that rejects anything is exit 1."""
    if not served(client):
        return EXIT_UNAVAILABLE, None, NOT_SERVED
    if body['op'] in GENERATING:
        from . import activation
        try:
            directive = client.directive()
            is_held = activation.held(directive)[0]
        except (ControlCenterError, AttributeError, KeyError, TypeError, ValueError):
            return EXIT_UNAVAILABLE, None, ('divergent-thinker: not consulted (held state unreadable); a generating '
                                            'op spends model calls, so none was made')
        if is_held:
            return EXIT_UNAVAILABLE, None, ('divergent-thinker: not consulted (held); this engine is held, so no '
                                            'generating op runs')
    try:
        answer = client.divergent(body)
    except ControlCenterError as error:
        return EXIT_UNAVAILABLE, None, refusal(error)
    if body['op'] == 'score' and flagged(answer):
        return EXIT_FLAGGED, answer, None
    return EXIT_OK, answer, None


def command(argv, client_factory):
    """growth.py divergent <op> [options]: print Control Center's JSON. Exit 0 ok, 1 a score flagged something,
    2 not served, unreachable, refused, capped or held (the reason on stderr)."""
    import argparse
    import sys
    p = argparse.ArgumentParser(prog='growth.py divergent',
                                description='divergent-thinker at will, through Control Center (engine/divergent.py)',
                                epilog='Cost: ' + '; '.join(op + ' ' + COST[op] for op in OPS) + '.')
    p.add_argument('op', choices=OPS)
    p.add_argument('--problem'); p.add_argument('--context'); p.add_argument('--idea')
    p.add_argument('--ideas-file'); p.add_argument('--obvious-file'); p.add_argument('--items-file')
    p.add_argument('--label', help='record: a short label for the batch')
    p.add_argument('--cliche', action='append', default=[])
    p.add_argument('--count', type=int); p.add_argument('--target'); p.add_argument('--temperament')
    p.add_argument('--lane', help='namespace ' + NAMESPACE + ':<lane>')
    p.add_argument('--judge', action='store_true', help='score: ask the judge too (spends model calls)')
    a = p.parse_args(argv)
    try:
        body = at_will_body(a.op, a.problem, a.context, a.idea,
                            items_of(a.ideas_file) if a.ideas_file else (),
                            items_of(a.obvious_file) if a.obvious_file else (),
                            items_of(a.items_file) if a.items_file else (),
                            a.cliche, a.count, a.target, a.temperament, a.lane, a.judge, a.label)
    except (ValueError, OSError) as error:
        p.error(str(error))
    try:
        client = client_factory()
    except ControlCenterError as error:
        print('divergent-thinker: not consulted (' + error.code + ')', file=sys.stderr)
        return EXIT_UNAVAILABLE
    code, answer, reason = at_will(client, body)
    if reason:
        print(reason, file=sys.stderr)
    if answer is not None:
        print(json.dumps(answer, ensure_ascii=False, indent=2))
    return code

