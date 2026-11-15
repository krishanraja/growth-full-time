"""The What-Works Analyst's learning register (docs/ENGINE-V2.md, crew row 9, and the
learning register paragraph).

Each learning is a claim that arm a beats arm b, the signal that measures it, the
evidence that would flip it, and what it is applied to. observe() adds a revision
whose status, z, intervals and reason are computed from the evidence, never written
by hand; earlier revisions are kept, and read() recomputes every one. Each arm's
exposure (what it had to earn its count, such as its number of posts) is recorded,
and z = (a - r * b) / sqrt(r * (a + b)) with r = exposure a / exposure b, which is
(a - b) / sqrt(a + b) when exposure is equal. 'confirmed' needs pre-registration, no
overlapping test, at least two matchweeks, at least 20 events per arm and z of 2 or
more for a; 'refuted' is the same bar with z of 2 or more for b; 'no_difference' is
the same clean bar with |z| under 2 once the planned matchweeks have passed;
anything else is 'directional'. The definition, the pre-registered flag and the
planned matchweeks are frozen at the first observation, and a test once marked
overlapping stays so: a changed experiment needs a new ID. Before the first live
post the register holds verdict analysis only.

The store is <local>/engine/learning.json, written with records.atomic_json under a
lock, with an immutable backup of the previous state per change, like
records.History. Nothing here posts, sends, schedules or spends.
"""
import contextlib
import copy
import csv
import io
import json
import math
from pathlib import Path
import re
import time

from . import reporting
from .attribution import poisson_interval, z_score
from .policy import sensitive_errors
from .records import atomic_json, fingerprint, instant, now

STATUSES = ('directional', 'confirmed', 'refuted', 'no_difference')
MIN_EVENTS = 20
MIN_MATCHWEEKS = 2
Z_BAR = 2
VERDICTS = ('post_it', 'edit', 'reject')
DEFINITION = ('claim', 'signal', 'flip_rule', 'applied_to')
ENTRY = ('id',) + DEFINITION + ('created_at', 'revisions')
EVIDENCE = ('a', 'b', 'matchweeks', 'preregistered', 'overlapping', 'planned_matchweeks', 'exposure_a', 'exposure_b')
DERIVED = ('n', 'z', 'interval_a', 'interval_b', 'status', 'why')
REVISION = ('revision', 'observed_at', 'definition_sha256') + DERIVED + EVIDENCE
# Fixed by the first observation: changing one after the data is seen is a new experiment.
FROZEN = ('preregistered', 'planned_matchweeks')
IDENTIFIER = re.compile(r'learning-([0-9]{3,6})')
CSV_FIELDS = ('id', 'status', 'claim', 'signal', 'revision', 'a', 'b', 'exposure_a', 'exposure_b', 'n', 'z',
              'interval_a', 'interval_b', 'matchweeks', 'planned_matchweeks', 'preregistered', 'overlapping',
              'flip_rule', 'applied_to', 'created_at', 'observed_at')
# Words too common to be a reason on their own.
STOP = {'the', 'and', 'but', 'for', 'with', 'too', 'not', 'are', 'was', 'its', "it's", 'this', 'that', 'than',
        'then', 'there', 'their', 'they', 'them', 'you', 'your', 'our', 'his', 'her', 'has', 'have', 'had',
        'does', 'did', 'can', 'could', 'should', 'would', 'will', 'more', 'less', 'much', 'some', 'any', 'all',
        'one', 'out', 'into', 'about', 'what', 'which', 'who', 'how', 'why', 'when', 'also', 'just', 'very',
        'from', 'been', 'being', 'were', 'only', 'here', 'like', 'make', 'needs', 'need'}


def _root(local):
    return Path(local) / 'engine'


def empty():
    return {'schema_version': 1, 'product': 'fulltime', 'learnings': {}}


def _text(value, what):
    if not isinstance(value, str) or not value.strip() or len(value) > 1000:
        raise ValueError(f'{what} must be non-empty text of up to 1,000 characters')
    return value.strip()


def _whole(value, what, least=0):
    if type(value) is not int or value < least:
        raise ValueError(f'{what} must be a whole number of at least {least}')
    return value


def _references(applied_to):
    if not isinstance(applied_to, list) or any(not isinstance(x, str) or not x.strip() for x in applied_to):
        raise ValueError('applied_to must be a list of non-empty references, such as a format or lock version')
    out = [x.strip() for x in applied_to]
    if len(set(out)) != len(out):
        raise ValueError('applied_to names one reference twice')
    return out


def _evidence(a, b, matchweeks, preregistered, overlapping, planned_matchweeks, exposure_a=1, exposure_b=1):
    evidence = {'a': _whole(a, 'arm a'), 'b': _whole(b, 'arm b'),
                'matchweeks': _whole(matchweeks, 'matchweeks'),
                'planned_matchweeks': _whole(planned_matchweeks, 'planned_matchweeks', MIN_MATCHWEEKS),
                'exposure_a': _whole(exposure_a, 'exposure_a', 1), 'exposure_b': _whole(exposure_b, 'exposure_b', 1)}
    for key, value in (('preregistered', preregistered), ('overlapping', overlapping)):
        if type(value) is not bool:
            raise ValueError(f'{key} must be true or false')
        evidence[key] = value
    return evidence


def _shown(z):
    """z cut toward zero at two places, so a shown z never crosses the bar its status was judged on."""
    return math.trunc(z * 100) / 100


def judge(a, b, matchweeks, preregistered, overlapping, planned_matchweeks, exposure_a=1, exposure_b=1):
    """(status, why) for this evidence, by the rule in the module docstring."""
    z = z_score(a, b, exposure_a, exposure_b)
    shown = _shown(z)
    powered = a >= MIN_EVENTS and b >= MIN_EVENTS
    clean = preregistered and not overlapping and matchweeks >= MIN_MATCHWEEKS and powered
    scaled = '' if exposure_a == exposure_b else f' over exposures {exposure_a} and {exposure_b}'
    if clean and z >= Z_BAR:
        return 'confirmed', (f'z {shown:.2f} for a, pre-registered, no overlap, {matchweeks} matchweeks, '
                             f'{a} against {b}{scaled}')
    if clean and z <= -Z_BAR:
        return 'refuted', (f'z {shown:.2f} for b, pre-registered, no overlap, {matchweeks} matchweeks, '
                           f'{a} against {b}{scaled}')
    if clean and matchweeks >= planned_matchweeks and abs(z) < Z_BAR:
        return 'no_difference', (f'|z| {abs(shown):.2f} under {Z_BAR}{scaled} after the planned '
                                 f'{planned_matchweeks} matchweeks: keep the cheaper arm')
    short = []
    if not preregistered:
        short.append('not pre-registered')
    if overlapping:
        short.append('overlaps another test')
    if matchweeks < MIN_MATCHWEEKS:
        short.append(f'{matchweeks} of {MIN_MATCHWEEKS} matchweeks')
    for arm, count in (('a', a), ('b', b)):
        if count < MIN_EVENTS:
            short.append(f'arm {arm} has {count} of {MIN_EVENTS} events')
    if abs(z) < Z_BAR:
        short.append(f'|z| {abs(shown):.2f} under {Z_BAR}{scaled}' + (', planned matchweeks still running'
                                                                      if matchweeks < planned_matchweeks else ''))
    return 'directional', 'directional only: ' + '; '.join(short or ['the evidence bar is not met'])


def _derived(evidence):
    """The fields computed from the evidence: never written by hand."""
    status, why = judge(*[evidence[k] for k in EVIDENCE])
    z = z_score(evidence['a'], evidence['b'], evidence['exposure_a'], evidence['exposure_b'])
    return {'n': evidence['a'] + evidence['b'], 'z': _shown(z), 'interval_a': list(poisson_interval(evidence['a'])),
            'interval_b': list(poisson_interval(evidence['b'])), 'status': status, 'why': why}


def _digest(entry):
    return fingerprint({k: entry[k] for k in DEFINITION})


def _changed(earlier, evidence):
    """What this evidence would change of what the first observation fixed."""
    if not earlier:
        return []
    out = [k for k in FROZEN if evidence[k] != earlier[0][k]]
    if any(r['overlapping'] for r in earlier) and not evidence['overlapping']:
        out.append('overlapping')
    return out


def _check_revision(revision, number, where, digest, earlier):
    if not isinstance(revision, dict) or set(revision) != set(REVISION) or revision['revision'] != number:
        raise ValueError(f'{where}: revision {number} is not in the register shape')
    try:
        evidence = _evidence(*[revision[k] for k in EVIDENCE])
        instant(revision['observed_at'])
    except ValueError as error:
        raise ValueError(f'{where}: revision {number} is not in the register shape ({error})') from None
    if revision['definition_sha256'] != digest:
        raise ValueError(f'{where}: the definition changed after revision {number} was observed; '
                         'a changed experiment needs a new ID')
    changed = _changed(earlier, evidence)
    if changed:
        raise ValueError(f'{where}: revision {number} changes {", ".join(changed)} after the first observation; '
                         'a changed experiment needs a new ID')
    if any(json.dumps(revision[k]) != json.dumps(v) for k, v in _derived(evidence).items()):
        raise ValueError(f'{where}: revision {number} has a status, z, count, interval or reason its evidence '
                         'does not give; they are computed, never written')


def validate(store):
    if not isinstance(store, dict) or set(store) != {'schema_version', 'product', 'learnings'} \
            or store['schema_version'] != 1 or store['product'] != 'fulltime' \
            or not isinstance(store['learnings'], dict):
        raise ValueError('invalid learning register schema or product; the register was not replaced')
    for key, entry in store['learnings'].items():
        if not isinstance(entry, dict) or set(entry) != set(ENTRY) or entry['id'] != key \
                or not isinstance(key, str) or not IDENTIFIER.fullmatch(key) \
                or not isinstance(entry['revisions'], list):
            raise ValueError(f'learning {key!r} is not in the register shape')
        try:
            for field in ('claim', 'signal', 'flip_rule'):
                _text(entry[field], field)
            _references(entry['applied_to'])
            instant(entry['created_at'])
        except ValueError as error:
            raise ValueError(f'learning {key!r} is not in the register shape ({error})') from None
        digest = _digest(entry)
        for number, revision in enumerate(entry['revisions'], start=1):
            _check_revision(revision, number, key, digest, entry['revisions'][:number - 1])
    if sensitive_errors(store):
        raise ValueError('the learning register contains private contacts or credential-like data')
    return store


def read(local):
    """The register as stored, or an empty one."""
    path = _root(local) / 'learning.json'
    if not path.exists():
        return empty()
    try:
        return validate(json.loads(path.read_text(encoding='utf-8')))
    except (ValueError, OSError) as error:
        raise ValueError('the learning register is unreadable; restore a validated backup before continuing') from error


@contextlib.contextmanager
def _transaction(local):
    root = _root(local)
    root.mkdir(parents=True, exist_ok=True)
    lock = root / '.learning-lock'
    deadline = time.monotonic() + 10
    while True:
        try:
            lock.mkdir()
            break
        except FileExistsError:
            if time.monotonic() >= deadline:
                raise ValueError('the learning register is locked; verify no writer is running before '
                                 'removing .learning-lock')
            time.sleep(0.02)
    try:
        path = root / 'learning.json'
        store = read(local)
        before = copy.deepcopy(store)
        yield store
        validate(store)
        if store != before or not path.exists():
            if path.exists():
                backup = root / 'learning-backups' / (fingerprint(before) + '.json')
                if not backup.exists():
                    atomic_json(backup, before)
            atomic_json(path, store)
    finally:
        lock.rmdir()


def add(local, claim, signal, flip_rule, applied_to):
    """A new learning, status directional until evidence arrives; returns its ID.
    The same definition added again returns the existing ID."""
    definition = {'claim': _text(claim, 'the claim'), 'signal': _text(signal, 'the signal'),
                  'flip_rule': _text(flip_rule, 'the flip rule'), 'applied_to': _references(applied_to)}
    if sensitive_errors(definition):
        raise ValueError('a learning holds aggregates and references only, never contacts or credentials')
    with _transaction(local) as store:
        for key, entry in store['learnings'].items():
            if {k: entry[k] for k in definition} == definition:
                return key
        numbers = [int(IDENTIFIER.fullmatch(k).group(1)) for k in store['learnings']]
        identifier = f'learning-{max(numbers, default=0) + 1:03d}'
        store['learnings'][identifier] = {'id': identifier, **definition, 'created_at': now(), 'revisions': []}
        return identifier


def observe(local, identifier, a, b, matchweeks, preregistered, overlapping, planned_matchweeks,
            exposure_a=1, exposure_b=1):
    """A new revision for this learning, with its status computed. a is the arm the
    claim says wins and b its control; exposure_a and exposure_b are what each arm had
    to earn its count, such as its number of posts (1 and 1 say they were equal). The
    first observation fixes preregistered and planned_matchweeks, and overlapping once
    true: a later change is refused, because a changed experiment needs a new ID. The
    same evidence twice returns the latest revision unchanged."""
    evidence = _evidence(a, b, matchweeks, preregistered, overlapping, planned_matchweeks, exposure_a, exposure_b)
    with _transaction(local) as store:
        entry = store['learnings'].get(identifier)
        if entry is None:
            raise ValueError(f'unknown learning {identifier!r}; add it first')
        changed = _changed(entry['revisions'], evidence)
        if changed:
            raise ValueError(f'{identifier} cannot change {", ".join(changed)} after its first observation; '
                             'a changed experiment needs a new ID')
        if entry['revisions'] and {k: entry['revisions'][-1][k] for k in EVIDENCE} == evidence:
            return copy.deepcopy(entry['revisions'][-1])
        revision = {'revision': len(entry['revisions']) + 1, 'observed_at': now(),
                    'definition_sha256': _digest(entry), **evidence, **_derived(evidence)}
        entry['revisions'].append(revision)
        return copy.deepcopy(revision)


# ---------------------------------------------------------------------------
# Reading the register.
# ---------------------------------------------------------------------------
def _entries(register):
    if isinstance(register, dict) and isinstance(register.get('learnings'), dict):
        return [register['learnings'][k] for k in sorted(register['learnings'])]
    if isinstance(register, list):
        return list(register)
    raise ValueError('a register is the store learning.read returns, or a list of its entries')


def _latest(entry):
    return entry['revisions'][-1] if entry.get('revisions') else None


def status(entry):
    """The entry's current status: its newest revision's, or directional before any evidence."""
    latest = _latest(entry)
    return latest['status'] if latest else 'directional'


def kill_double_down(register):
    """{'kill': [...], 'double_down': [...]}: refuted learnings to stop relying on and
    confirmed ones to do more of. Each item carries a line of at most 1,000 characters
    that always keeps "What flips it"; proposal(item) turns it into the weekly ask."""
    out = {'kill': [], 'double_down': []}
    for entry in _entries(register):
        latest = _latest(entry)
        if not latest or latest['status'] not in ('confirmed', 'refuted'):
            continue
        confirmed = latest['status'] == 'confirmed'
        exposure = (latest.get('exposure_a', 1), latest.get('exposure_b', 1))
        evidence = (f'z {latest["z"]}, {latest["a"]} against {latest["b"]}'
                    + ('' if exposure[0] == exposure[1] else f' on exposures {exposure[0]} and {exposure[1]}')
                    + f' over {latest["matchweeks"]} matchweeks')
        claim = entry['claim'][:400]
        line = ((f'Double down on {entry["id"]}: "{claim}" is confirmed ({evidence}).' if confirmed else
                 f'Stop relying on {entry["id"]}: "{claim}" was refuted ({evidence}).')
                + f' What flips it: {entry["flip_rule"]}')
        out['double_down' if confirmed else 'kill'].append(
            {'id': entry['id'], 'claim': entry['claim'], 'status': latest['status'], 'z': latest['z'],
             'a': latest['a'], 'b': latest['b'], 'applied_to': list(entry['applied_to']),
             'flip_rule': entry['flip_rule'], 'line': line[:1000]})
    return out


def proposal(item):
    """The weekly strategy ask for one kill_double_down item: a refuted learning
    through reporting.kill_proposal, a confirmed one titled as doing more of it."""
    if not isinstance(item, dict) or item.get('status') not in ('confirmed', 'refuted') \
            or not isinstance(item.get('line'), str):
        raise ValueError('only a kill_double_down item, confirmed or refuted, becomes a weekly proposal')
    if item['status'] == 'refuted':
        return reporting.kill_proposal(item['line'])
    pid = f'{reporting.SLUG}:double-down:{reporting.canonical_sha256(item["line"])[:12]}'
    return reporting._proposal(pid, 'Weekly review: do more of this', item['line'], 'advice', 'strategy',
                               {'proposal_id': pid, 'double_down': item['line']}, 'ruling_recorded', pid)


def _cell(value):
    """Text that a spreadsheet could read as a formula is kept as text."""
    return "'" + value if isinstance(value, str) and value[:1] in ('=', '+', '-', '@', '\t', '\r') else value


def export_csv(register):
    """register.csv text for Growth Build/04_Learning: one row per learning at its
    newest revision, LF line endings, rows by ID."""
    out = io.StringIO()
    writer = csv.writer(out, lineterminator='\n')
    writer.writerow(CSV_FIELDS)
    for entry in sorted(_entries(register), key=lambda e: e['id']):
        latest = _latest(entry) or {}
        span = lambda key: '' if not latest else f'{latest[key][0]} to {latest[key][1]}'
        flag = lambda key: '' if not latest else ('yes' if latest[key] else 'no')
        writer.writerow([
            entry['id'], status(entry), _cell(entry['claim']), _cell(entry['signal']),
            latest.get('revision', 0), latest.get('a', ''), latest.get('b', ''), latest.get('exposure_a', ''),
            latest.get('exposure_b', ''), latest.get('n', ''), latest.get('z', ''), span('interval_a'),
            span('interval_b'), latest.get('matchweeks', ''), latest.get('planned_matchweeks', ''),
            flag('preregistered'), flag('overlapping'), _cell(entry['flip_rule']),
            _cell('; '.join(entry['applied_to'])), _cell(entry['created_at']), _cell(latest.get('observed_at', ''))])
    return out.getvalue()


def blocked_locks(register, locks):
    """The lock versions that cite a refuted learning, in the order given. locks is a
    list of {'lock_version', 'learnings': [ids]} or a mapping of lock_version to ids.
    A blocked lock needs a new lock version that drops the refuted learning."""
    refuted = {e['id'] for e in _entries(register) if status(e) == 'refuted'}
    if isinstance(locks, dict):
        pairs = list(locks.items())
    elif isinstance(locks, list) and all(isinstance(x, dict) for x in locks):
        pairs = [(x.get('lock_version'), x.get('learnings')) for x in locks]
    else:
        raise ValueError('locks must be a list of {lock_version, learnings} or a mapping of version to IDs')
    out = []
    for version, cited in pairs:
        if not isinstance(version, str) or not version or not isinstance(cited, list):
            raise ValueError('each lock needs a lock_version and a list of the learnings it cites')
        if refuted & set(map(str, cited)) and version not in out:
            out.append(version)
    return out


# ---------------------------------------------------------------------------
# Verdict analysis: which of Krish's edits and rejects repeat, and why.
# ---------------------------------------------------------------------------
def _words(note):
    if not isinstance(note, str):
        return set()
    words = {w.strip("'-") for w in re.findall(r"[a-z][a-z'-]*", note.lower())}
    return {w for w in words if len(w) >= 3 and w not in STOP}


def verdict_analysis(verdicts):
    """Counts of edit and reject verdicts by format, by AI Pundit and by the words in
    their notes, flagging every reason seen at least twice. Each verdict is a dict with
    verdict (post_it, edit or reject), format_id, pundit and note; post it is not counted."""
    out = {'edit': 0, 'reject': 0, 'by_format': {}, 'by_pundit': {}, 'by_word': {}, 'repeated': []}
    for number, verdict in enumerate(verdicts or [], start=1):
        if not isinstance(verdict, dict) or verdict.get('verdict') not in VERDICTS:
            raise ValueError(f'verdict {number} must be post_it, edit or reject')
        kind = verdict['verdict']
        if kind == 'post_it':
            continue
        out[kind] += 1
        for field, bucket in (('format_id', 'by_format'), ('pundit', 'by_pundit')):
            name = verdict.get(field) if isinstance(verdict.get(field), str) and verdict.get(field) else 'unknown'
            out[bucket].setdefault(name, {'edit': 0, 'reject': 0})[kind] += 1
        for word in sorted(_words(verdict.get('note'))):
            out['by_word'].setdefault(word, {'edit': 0, 'reject': 0})[kind] += 1
    totals = {word: c['edit'] + c['reject'] for word, c in out['by_word'].items()}
    out['repeated'] = [{'reason': word, 'count': count, **out['by_word'][word]}
                       for word, count in sorted(totals.items(), key=lambda pair: (-pair[1], pair[0]))
                       if count >= 2]
    return out


# ---------------------------------------------------------------------------
# Planning a test before it is registered (the Claude Ads review, 2026-11-15,
# docs/CLAUDE-ADS.md: "calculate sample and duration from declared assumptions;
# disclose approximations"). Planning is never evidence: nothing here is written
# to the register, and a plan's numbers are assumptions until the export measures them.
# ---------------------------------------------------------------------------
POWER = 0.8
APPROXIMATION = ('Normal approximation to the conditional Poisson test judge() applies: expected z after T '
                 'matchweeks is k * sqrt(T) with k = (rate_a - r * rate_b) / sqrt(r * (rate_a + rate_b)) and '
                 'r = exposure_a / exposure_b. The chance is of z crossing the bar in the assumed direction. '
                 'The rates are declared assumptions, not measurements.')


def _rate(value, what):
    if type(value) not in (int, float) or not math.isfinite(value) or value <= 0:
        raise ValueError(f'{what} must be a finite number above zero')
    return float(value)


def _chance(k, weeks):
    """The approximate chance that z crosses the bar in the assumed direction after `weeks`."""
    from statistics import NormalDist
    return round(1 - NormalDist().cdf(Z_BAR - abs(k) * math.sqrt(weeks)), 2)


def plan(rate_a, rate_b, exposure_a=1, exposure_b=1, max_matchweeks=None, power=POWER):
    """How many matchweeks a two-arm test needs before judge() can call it, from declared
    weekly rates (expected events a matchweek in each arm) and each arm's exposure a
    matchweek. The test needs the longest of: MIN_MATCHWEEKS, enough weeks for the smaller
    arm to reach MIN_EVENTS, and enough weeks for the chance of crossing Z_BAR to reach
    `power`. With `max_matchweeks`, it also says whether the test fits and the smallest
    lift it could confirm in that time."""
    from statistics import NormalDist
    rate_a, rate_b = _rate(rate_a, 'rate_a'), _rate(rate_b, 'rate_b')
    exposure_a, exposure_b = _rate(exposure_a, 'exposure_a'), _rate(exposure_b, 'exposure_b')
    if type(power) not in (int, float) or not 0.5 <= power < 1:
        raise ValueError('power must be at least 0.5 and under 1')
    if max_matchweeks is not None:
        _whole(max_matchweeks, 'max_matchweeks', MIN_MATCHWEEKS)
    ratio = exposure_a / exposure_b
    k = (rate_a - ratio * rate_b) / math.sqrt(ratio * (rate_a + rate_b))
    needs = {'minimum': MIN_MATCHWEEKS, 'events': math.ceil(MIN_EVENTS / min(rate_a, rate_b) - 1e-9)}
    target = Z_BAR + NormalDist().inv_cdf(power)
    lift = round(rate_a / (ratio * rate_b), 2)
    out = {'rate_a': rate_a, 'rate_b': rate_b, 'exposure_a': exposure_a, 'exposure_b': exposure_b,
           'assumed_lift': lift, 'power': power, 'bar': {'z': Z_BAR, 'events_per_arm': MIN_EVENTS,
                                                          'matchweeks': MIN_MATCHWEEKS},
           'approximation': APPROXIMATION, 'evidence': False}
    if abs(k) < 1e-12:
        out.update(matchweeks_needed=None, limited_by='no_difference_assumed',
                   why=(f'Equal rates assumed: the test can only end no_difference, after at least '
                        f'{max(needs.values())} matchweeks.'))
    else:
        needs['power'] = math.ceil((target / abs(k)) ** 2 - 1e-9)
        weeks = max(needs.values())
        limited = max(needs, key=lambda key: (needs[key], key == 'power'))
        winner = 'a' if k > 0 else 'b'
        out.update(matchweeks_needed=weeks, limited_by=limited, expected_winner=winner,
                   expected_at_end={'a': round(rate_a * weeks, 1), 'b': round(rate_b * weeks, 1),
                                    'z': _shown(k * math.sqrt(weeks))},
                   chance_of_a_call=_chance(k, weeks),
                   why=(f'{weeks} matchweeks, set by {limited}: arm {winner} is assumed {lift}x per exposure, '
                        f'so z is expected to reach {_shown(k * math.sqrt(weeks)):.2f}; '
                        f'{"confirmed" if winner == "a" else "refuted"} is then about '
                        f'{round(_chance(k, weeks) * 100)}% likely.'))
    if max_matchweeks is None:
        return out
    if out['matchweeks_needed'] is None:
        fits = max(needs.values()) <= max_matchweeks   # it can end no_difference in time
    else:
        fits = out['matchweeks_needed'] <= max_matchweeks
    out.update(max_matchweeks=max_matchweeks, fits=fits)
    if out['matchweeks_needed'] is not None:
        out['chance_by_max'] = _chance(k, max_matchweeks)
    if rate_b * max_matchweeks < MIN_EVENTS:
        out['smallest_confirmable_lift'] = None
        out['why'] += (f' In {max_matchweeks} matchweeks arm b reaches about {round(rate_b * max_matchweeks, 1)} '
                       f'events, under {MIN_EVENTS}: no lift can be confirmed in time. Pool arms or test for longer.')
        return out
    c = target ** 2 / max_matchweeks
    gap = (c * ratio + math.sqrt((c * ratio) ** 2 + 4 * c * ratio * rate_b * (ratio + 1))) / 2
    smallest = (ratio * rate_b + gap) / (ratio * rate_b)
    out['smallest_confirmable_lift'] = math.ceil(smallest * 100) / 100
    if out['matchweeks_needed'] is None or not fits:
        out['why'] += ((f' It does not fit in {max_matchweeks} matchweeks: in that time' if not fits
                        else f' In {max_matchweeks} matchweeks') + ' only a lift of about '
                       f'{out["smallest_confirmable_lift"]}x or more is likely to be confirmed.')
    return out


def cost_per_event(spend_gbp, events):
    """What each counted event cost, with the band the count's rough 95% interval gives:
    spend / count, and spend over each end of the count's interval. Under MIN_EVENTS the
    reading is directional. A missing count stays missing and zero events give no cost,
    never an infinite one (Claude Ads: never hide a division by zero)."""
    if type(spend_gbp) not in (int, float) or not math.isfinite(spend_gbp) or spend_gbp < 0:
        raise ValueError('spend_gbp must be a finite amount of zero or more')
    out = {'spend_gbp': round(float(spend_gbp), 2), 'events': events}
    if events is None:
        return {**out, 'cost_gbp': None, 'band_gbp': None, 'why': 'events missing: no cost per event'}
    _whole(events, 'events')
    if events == 0:
        return {**out, 'cost_gbp': None, 'band_gbp': None,
                'why': 'no events counted: there is no cost per event to report'}
    low, high = poisson_interval(events)
    band = [round(spend_gbp / high, 2), round(spend_gbp / low, 2) if low > 0 else None]
    reading = 'directional only' if events < MIN_EVENTS else 'readable'
    return {**out, 'cost_gbp': round(spend_gbp / events, 2), 'band_gbp': band, 'reading': reading,
            'why': (f'£{spend_gbp / events:.2f} each; the count\'s rough 95% interval {low} to {high} gives '
                    f'£{band[0]:.2f} to ' + (f'£{band[1]:.2f}' if band[1] is not None else 'no upper bound')
                    + (f'. Readable: {events} events, at least the {MIN_EVENTS} the bar reads.' if events >= MIN_EVENTS
                       else f'. Directional only: {events} of the {MIN_EVENTS} events the bar reads.'))}


def spend_plan(budget_gbp, cost_low_gbp, cost_high_gbp):
    """Before a spend: the events a budget buys across an assumed cost band, and the cost per
    event at which it still reaches MIN_EVENTS, the least the What-Works bar reads."""
    budget = _rate(budget_gbp, 'budget_gbp')
    low, high = _rate(cost_low_gbp, 'cost_low_gbp'), _rate(cost_high_gbp, 'cost_high_gbp')
    if low > high:
        raise ValueError('cost_low_gbp must not be above cost_high_gbp')
    events = [round(budget / high, 1), round(budget / low, 1)]
    ceiling = round(budget / MIN_EVENTS, 2)
    readable = 'yes' if events[0] >= MIN_EVENTS else ('no' if events[1] < MIN_EVENTS else 'only at the cheap end')
    return {'budget_gbp': budget, 'assumed_cost_band_gbp': [low, high], 'expected_events': events,
            'readable_if_cost_at_most_gbp': ceiling, 'readable': readable, 'evidence': False,
            'why': (f'£{budget:.0f} buys about {events[0]} to {events[1]} events at £{low:.2f} to £{high:.2f} each. '
                    f'It reaches {MIN_EVENTS} events, the least the What-Works bar reads, only if each costs '
                    f'£{ceiling:.2f} or less. Assumed costs, not measurements.')}
