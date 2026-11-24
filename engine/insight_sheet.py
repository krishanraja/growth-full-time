"""The insight desk's sheet for Full Time (Ruling, Krish, 2026-11-24): checks only.

The method lives in ai-harness's insight-desk skill; config/insight-desk.json is this
engine's adapter. This module checks an insight sheet (insight-sheet/1) with the standard
library, adds Full Time's own rules, and builds the seed `spec propose --insight` hangs on
the G1 plan. It reads and reports. It never posts, sends, schedules or spends, and a sheet
is never committed: sheets live in local/insight/.

Full Time's rules on top of the skill's:
  - venture and repository are this engine's;
  - no humour engine consult (the adapter says humour is unavailable);
  - the sheet's North Star urgency and reading agree with NOW.md, and while NOW.md says U4
    with no current reading, every idea is a measurement idea;
  - a seeded week names the objective its lead measures.
"""
import datetime as dt
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent.parent
ADAPTER = HERE / 'config' / 'insight-desk.json'
SCHEMA = 'insight-sheet/1'

TOP_KEYS = ('schema', 'venture', 'repo', 'harness_skill_sha', 'made_at', 'north_star', 'stall_check',
            'insights', 'chosen_insight', 'discarded_obvious', 'ideas', 'consults', 'lead',
            'blind_passes', 'sheet_sha256')
DIAGNOSES = ('idea', 'distribution', 'offer', 'attribution', 'measurement')
LEVELS = ('execution', 'campaign', 'platform', 'business', 'measurement')
TEST_KEYS = ('specificity', 'share', 'analogue', 'floor', 'kill_the_favourite')
RESULTS = ('pass', 'fail', 'unavailable')
CONSULT_RESULTS = ('pass', 'flagged', 'unavailable')
ENGINES = ('divergent-thinker', 'humour-engine')
IDEA_KEYS = ('id', 'claim', 'mechanic', 'idea_level', 'method', 'channel_role', 'conversion_path',
             'kill_condition', 'tests')
ADAPTER_KEYS = ('schema', 'skill', 'venture', 'repo', 'north_star', 'humour', 'divergent', 'reads',
                'first_sheet', 'sheets', 'hook', 'approval_path')
ID_RE = re.compile(r'^[a-z0-9][a-z0-9-]{0,39}$')
METHOD_RE = re.compile(r'^[a-z0-9][a-z0-9-]*$')
REPO_RE = re.compile(r'^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$')
SHA1_RE = re.compile(r'^[0-9a-f]{40}$')
SHA256_RE = re.compile(r'^[0-9a-f]{64}$')
SCORE_KEY = re.compile(r'(?i)^(score|scores|rating|points|weight|weighted_total|total)$')
EM_DASH = chr(0x2014)
# The objective each measurement lead is measured by: the North Star metric itself.
MEASURED_BY = {'measurement': 'attributed_new_completers'}


def load_json(path):
    def refuse(constant):
        raise ValueError(f'{path}: {constant} is not a number')
    return json.loads(Path(path).read_text(encoding='utf-8'), parse_constant=refuse)


def load_adapter(path=ADAPTER):
    return load_json(path)


def adapter_errors(adapter):
    """Every reason the adapter is wrong for this engine. Empty means it holds."""
    if not isinstance(adapter, dict):
        return ['config/insight-desk.json is not a JSON object']
    out = [f'config/insight-desk.json: {key} is required' for key in ADAPTER_KEYS if key not in adapter]
    if out:
        return out
    if adapter['schema'] != 'insight-desk-adapter/1':
        out.append('config/insight-desk.json: schema must be insight-desk-adapter/1')
    if (adapter.get('skill') or {}).get('name') != 'insight-desk':
        out.append('config/insight-desk.json: skill.name must be insight-desk')
    if adapter['venture'] != 'fulltime' or adapter['repo'] != 'krishanraja/growth-fulltime':
        out.append('config/insight-desk.json: venture and repo must be this engine (fulltime, krishanraja/growth-fulltime)')
    if (adapter.get('humour') or {}).get('allowed') is not False:
        out.append('config/insight-desk.json: humour is unavailable for Full Time; allowed must be false')
    divergent = adapter.get('divergent') or {}
    if divergent.get('route') != 'connector' or divergent.get('namespace') != 'growth-fulltime:ideas':
        out.append('config/insight-desk.json: divergent runs through the connector in growth-fulltime:ideas only')
    if divergent.get('scheduled_run') != 'unavailable':
        out.append('config/insight-desk.json: a scheduled run has no divergent client, so it records unavailable')
    if (adapter.get('first_sheet') or {}).get('idea_level') != 'measurement':
        out.append('config/insight-desk.json: the first sheet is a measurement idea while the number is unmeasured')
    if not str(adapter.get('sheets') or '').startswith('local/'):
        out.append('config/insight-desk.json: sheets live under local/, never committed')
    if '--insight' not in str((adapter.get('hook') or {}).get('command') or ''):
        out.append('config/insight-desk.json: hook.command must name spec propose --insight')
    for key, value in (adapter.get('reads') or {}).items():
        for name in value if isinstance(value, list) else [value]:
            if not str(name).startswith('local/') and not (HERE / name).exists():
                out.append(f'config/insight-desk.json: reads.{key} names {name}, which is not in the repository')
    _no_em_dash(adapter, 'config/insight-desk.json', out)
    return out


def methods_from(skill_dir):
    """The method slugs the skill's references/methods-by-category.md names, when a checkout is at hand."""
    text = (Path(skill_dir) / 'references' / 'methods-by-category.md').read_text(encoding='utf-8')
    return set(re.findall(r'(?m)^### `([a-z0-9-]+)`', text))


def now_state(root=HERE):
    """The north-star-state block of NOW.md as a dict, or None when it cannot be read."""
    from .invariants import STATE
    try:
        text = (Path(root) / 'NOW.md').read_text(encoding='utf-8')
    except OSError:
        return None
    found = STATE.findall(text)
    if len(found) != 1:
        return None
    try:
        return json.loads(found[0][0])
    except ValueError:
        return None


def canonical(sheet):
    body = {k: v for k, v in sheet.items() if k != 'sheet_sha256'}
    return json.dumps(body, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def sheet_sha(sheet):
    """SHA-256 of the canonical sheet without sheet_sha256, as the skill computes it."""
    return hashlib.sha256(canonical(sheet)).hexdigest()


def _filled(value):
    return isinstance(value, str) and value.strip() != ''


def _is_date(value):
    try:
        dt.date.fromisoformat(value)
        return isinstance(value, str)
    except (TypeError, ValueError):
        return False


def _is_datetime(value):
    if not isinstance(value, str) or 'T' not in value:
        return False
    try:
        dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
        return True
    except ValueError:
        return False


def _int(value):
    return isinstance(value, int) and not isinstance(value, bool)


def _no_em_dash(node, where, out):
    if isinstance(node, dict):
        for key, value in node.items():
            _no_em_dash(value, f'{where}.{key}', out)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            _no_em_dash(value, f'{where}[{i}]', out)
    elif isinstance(node, str) and EM_DASH in node:
        out.append(f'{where}: carries an em dash')


def _no_scores(node, where, out):
    if isinstance(node, dict):
        for key, value in node.items():
            if SCORE_KEY.match(str(key)):
                out.append(f'{where}.{key}: no scores; the sheet carries results and reasons only')
            _no_scores(value, f'{where}.{key}', out)
    elif isinstance(node, list):
        for i, value in enumerate(node):
            _no_scores(value, f'{where}[{i}]', out)


def _test(label, test, out, analogue=False):
    if not isinstance(test, dict):
        out.append(f'{label}: missing')
        return
    allowed = {'result', 'reason'} | ({'url', 'read_at'} if analogue else set())
    if set(test) - allowed:
        out.append(f'{label}: unexpected fields {", ".join(sorted(set(test) - allowed))}')
    if test.get('result') not in RESULTS:
        out.append(f'{label}: result must be pass, fail or unavailable (got {test.get("result")!r})')
    if not _filled(test.get('reason')):
        out.append(f'{label}: needs a reason')
    if analogue:
        for key in ('url', 'read_at'):
            if key not in test:
                out.append(f'{label}: needs {key} (null when none was found)')
        if test.get('result') == 'pass':
            if not _filled(test.get('url')):
                out.append(f'{label}: a passing analogue is linked')
            if not _is_date(test.get('read_at')):
                out.append(f'{label}: a passing analogue records the date it was read')


def _idea(i, idea, methods, out):
    label = f'ideas[{i}]'
    if not isinstance(idea, dict):
        out.append(f'{label}: not an object')
        return
    missing = [k for k in IDEA_KEYS if k not in idea]
    if missing:
        out.append(f'{label}: missing {", ".join(missing)}')
    if set(idea) - set(IDEA_KEYS):
        out.append(f'{label}: unexpected fields {", ".join(sorted(set(idea) - set(IDEA_KEYS)))}')
    if not (isinstance(idea.get('id'), str) and ID_RE.match(idea['id'])):
        out.append(f'{label}: id must be lower-case letters, digits and hyphens')
    for key in ('claim', 'mechanic', 'channel_role', 'kill_condition'):
        if key in idea and not _filled(idea[key]):
            out.append(f'{label}: {key} is empty')
    if idea.get('idea_level') not in LEVELS:
        out.append(f'{label}: idea_level must be one of {", ".join(LEVELS)}')
    method = idea.get('method')
    if not (isinstance(method, str) and METHOD_RE.match(method)):
        out.append(f'{label}: method must be a method slug from the skill')
    elif methods is not None and method not in methods:
        out.append(f'{label}: method {method!r} is not in the skill\'s methods-by-category.md')
    path = idea.get('conversion_path')
    if not isinstance(path, dict) or not all(_filled(path.get(k)) for k in ('offer', 'link', 'why_act')):
        out.append(f'{label}: an idea with no full conversion path (offer, link, why_act) is held off the sheet')
    elif set(path) - {'offer', 'link', 'why_act'}:
        out.append(f'{label}: conversion_path has unexpected fields')
    tests = idea.get('tests')
    if not isinstance(tests, dict):
        out.append(f'{label}: tests missing')
        return
    if set(tests) - set(TEST_KEYS):
        out.append(f'{label}: unexpected tests {", ".join(sorted(set(tests) - set(TEST_KEYS)))}')
    for key in TEST_KEYS:
        _test(f'{label}.tests.{key}', tests.get(key), out, analogue=(key == 'analogue'))


def _insight(i, insight, out):
    label = f'insights[{i}]'
    if not isinstance(insight, dict):
        out.append(f'{label}: not an object')
        return
    for key in ('audience', 'wants', 'but', 'because'):
        if not _filled(insight.get(key)):
            out.append(f'{label}: {key} is empty')
    extra = set(insight) - {'audience', 'wants', 'but', 'because', 'source', 'read_at', 'assumption'}
    if extra:
        out.append(f'{label}: unexpected fields {", ".join(sorted(extra))}')
    sourced, assumed = 'source' in insight or 'read_at' in insight, 'assumption' in insight
    if sourced and assumed:
        out.append(f'{label}: either a source and read_at, or assumption: true, never both')
    elif assumed:
        if insight['assumption'] is not True:
            out.append(f'{label}: assumption must be true when present')
    elif not (_filled(insight.get('source')) and _is_date(insight.get('read_at'))):
        out.append(f'{label}: needs a source and the date it was read, or assumption: true')


def skill_errors(sheet, methods=None):
    """The skill's own rules (insight-sheet/1), in plain words. Empty means the sheet holds."""
    out = []
    if not isinstance(sheet, dict):
        return ['the sheet is not a JSON object']
    missing = [k for k in TOP_KEYS if k not in sheet]
    if missing:
        out.append(f'missing {", ".join(missing)}')
    if set(sheet) - set(TOP_KEYS):
        out.append(f'unexpected fields {", ".join(sorted(set(sheet) - set(TOP_KEYS)))}')
    if sheet.get('schema') != SCHEMA:
        out.append(f'schema must be {SCHEMA}')
    if not _filled(sheet.get('venture')):
        out.append('venture is empty')
    if not (isinstance(sheet.get('repo'), str) and REPO_RE.match(sheet['repo'])):
        out.append('repo must be owner/name')
    if not (isinstance(sheet.get('harness_skill_sha'), str) and SHA1_RE.match(sheet['harness_skill_sha'])):
        out.append('harness_skill_sha must be the 40-character commit the skill was read at')
    if not _is_datetime(sheet.get('made_at')):
        out.append('made_at must be an ISO date-time')

    ns, urgency, current = sheet.get('north_star'), None, None
    if not isinstance(ns, dict) or set(ns) != {'metric', 'urgency', 'current', 'as_of'}:
        out.append('north_star needs exactly metric, urgency, current and as_of')
    else:
        urgency, current = ns.get('urgency'), ns.get('current')
        if not _filled(ns.get('metric')):
            out.append('north_star.metric is empty')
        if not (_int(urgency) and 1 <= urgency <= 5):
            out.append('north_star.urgency must be 1 to 5')
        if current is not None and (isinstance(current, bool) or not isinstance(current, (int, float))):
            out.append('north_star.current must be a number or null')
        if ns.get('as_of') is not None and not _is_date(ns.get('as_of')):
            out.append('north_star.as_of must be a date or null')

    stall, diagnosis = sheet.get('stall_check'), None
    if not isinstance(stall, dict) or set(stall) != {'diagnosis', 'evidence'}:
        out.append('stall_check needs exactly diagnosis and evidence')
    else:
        diagnosis = stall.get('diagnosis')
        if diagnosis not in DIAGNOSES:
            out.append(f'stall_check.diagnosis must be one of {", ".join(DIAGNOSES)}')
        elif diagnosis not in ('idea', 'measurement'):
            out.append(f'the stall is {diagnosis}, not the idea; the desk stops and makes no sheet')
        if not _filled(stall.get('evidence')):
            out.append('stall_check.evidence is empty')

    insights = sheet.get('insights')
    if not isinstance(insights, list) or not 1 <= len(insights) <= 3:
        out.append('insights must hold one to three lines')
        insights = insights if isinstance(insights, list) else []
    for i, insight in enumerate(insights):
        _insight(i, insight, out)
    chosen = sheet.get('chosen_insight')
    if not (_int(chosen) and 0 <= chosen < len(insights)):
        out.append('chosen_insight must point at one of the insights')

    obvious = sheet.get('discarded_obvious')
    if not (isinstance(obvious, list) and len(obvious) == 3 and all(_filled(o) for o in obvious)):
        out.append('discarded_obvious must hold exactly three ideas')
        obvious = []

    ideas = sheet.get('ideas')
    if not isinstance(ideas, list) or not 1 <= len(ideas) <= 3:
        out.append('ideas must hold one to three ideas')
        ideas = ideas if isinstance(ideas, list) else []
    for i, idea in enumerate(ideas):
        _idea(i, idea, methods, out)
    by_id = {idea.get('id'): idea for idea in ideas if isinstance(idea, dict)}
    if len(by_id) != len(ideas):
        out.append('idea ids must be unique')
    plain = {' '.join(str(o).lower().split()) for o in obvious}
    for idea in by_id.values():
        if ' '.join(str(idea.get('claim', '')).lower().split()) in plain:
            out.append(f'idea {idea.get("id")}: restates a discarded obvious idea')
    if diagnosis == 'measurement' or (urgency == 4 and current is None):
        for idea in by_id.values():
            if idea.get('idea_level') != 'measurement':
                out.append(f'idea {idea.get("id")}: nothing is measured, so every idea is a measurement idea')

    consults = sheet.get('consults')
    if not isinstance(consults, list):
        out.append('consults must be a list (empty when no engine was called)')
        consults = []
    for i, consult in enumerate(consults):
        if not isinstance(consult, dict) or set(consult) != {'engine', 'op', 'result', 'ref'}:
            out.append(f'consults[{i}]: needs exactly engine, op, result and ref')
            continue
        if consult['engine'] not in ENGINES:
            out.append(f'consults[{i}]: engine must be one of {", ".join(ENGINES)}')
        if consult['result'] not in CONSULT_RESULTS:
            out.append(f'consults[{i}]: result must be pass, flagged or unavailable; exit 2 is unavailable, never pass')
        if not _filled(consult['op']) or not _filled(consult['ref']):
            out.append(f'consults[{i}]: op and ref are filled')

    passes = sheet.get('blind_passes')
    if not isinstance(passes, list) or len(passes) != 2:
        out.append('blind_passes must hold exactly two passes')
        passes = []
    ids = sorted(map(str, by_id))
    for i, blind in enumerate(passes):
        if not isinstance(blind, dict) or set(blind) != {'reader', 'order', 'lead'}:
            out.append(f'blind_passes[{i}]: needs exactly reader, order and lead')
            continue
        if not _filled(blind['reader']):
            out.append(f'blind_passes[{i}]: name the reader')
        if not isinstance(blind['order'], list) or sorted(map(str, blind['order'])) != ids:
            out.append(f'blind_passes[{i}]: order must list every idea id once')
        if blind['lead'] is not None and blind['lead'] not in by_id:
            out.append(f'blind_passes[{i}]: lead is not an idea on the sheet')
    if len(passes) == 2 and all(isinstance(p, dict) for p in passes):
        if len(ids) > 1 and passes[0].get('order') == passes[1].get('order'):
            out.append('blind_passes: the two orders must be shuffled differently')
        if any(p.get('reader') in ('writer', 'author') for p in passes):
            out.append('blind_passes: the reader is never the writer of the ideas')

    lead = sheet.get('lead')
    if lead is not None:
        if lead not in by_id:
            out.append('lead is not an idea on the sheet')
        else:
            if not passes or any(isinstance(p, dict) and p.get('lead') != lead for p in passes):
                out.append('lead: both blind passes must pick the same lead; otherwise lead is null')
            tests = by_id[lead].get('tests') or {}
            for key in TEST_KEYS:
                result = (tests.get(key) or {}).get('result')
                if result != 'pass':
                    out.append(f'lead {lead}: {key} is {result}; an idea leads only when every test passed')

    _no_scores(sheet, 'sheet', out)
    _no_em_dash(sheet, 'sheet', out)
    claimed = sheet.get('sheet_sha256')
    if not (isinstance(claimed, str) and SHA256_RE.match(claimed)):
        out.append('sheet_sha256 must be 64 lower-case hex characters')
    elif claimed != sheet_sha(sheet):
        out.append('sheet_sha256 does not match the sheet; recompute it')
    return out


def engine_errors(sheet, adapter=None, state=None):
    """Full Time's own rules, read from the adapter and NOW.md's north-star-state line."""
    adapter = adapter if adapter is not None else load_adapter()
    out = []
    if not isinstance(sheet, dict):
        return out
    if sheet.get('venture') != adapter.get('venture') or sheet.get('repo') != adapter.get('repo'):
        out.append(f'the sheet is for {sheet.get("venture")} ({sheet.get("repo")}), not this engine '
                   f'({adapter.get("venture")}, {adapter.get("repo")})')
    if not (adapter.get('humour') or {}).get('allowed'):
        for consult in sheet.get('consults') or []:
            if isinstance(consult, dict) and consult.get('engine') == 'humour-engine':
                out.append('consults: the humour engine is unavailable for Full Time; no humour call is made')
    ns = sheet.get('north_star') if isinstance(sheet.get('north_star'), dict) else {}
    metric = (adapter.get('north_star') or {}).get('metric')
    if metric and ns.get('metric') != metric:
        out.append(f'north_star.metric must be {metric}, the number NOW.md tracks')
    if state is None:
        out.append('NOW.md has no readable north-star-state line; the desk stops at its gate')
        return out
    if ns.get('urgency') != state.get('urgency'):
        out.append(f'north_star.urgency is {ns.get("urgency")}; NOW.md says U{state.get("urgency")}')
    if ns.get('current') != state.get('current'):
        out.append(f'north_star.current is {ns.get("current")}; NOW.md says {state.get("current")}')
    if state.get('urgency') == 4 and state.get('current') is None:
        for idea in sheet.get('ideas') or []:
            if isinstance(idea, dict) and idea.get('idea_level') != 'measurement':
                out.append(f'idea {idea.get("id")}: NOW.md says U4 and unmeasured, so the sheet holds measurement ideas only')
    return out


def validate(sheet, adapter=None, state=None, methods=None, root=HERE):
    """Every reason the sheet is refused for this engine. Empty means valid."""
    state = now_state(root) if state is None else state
    return skill_errors(sheet, methods) + engine_errors(sheet, adapter, state)


def seed(campaign, sheet, adapter=None, state=None, methods=None, root=HERE):
    """What the G1 plan carries from a valid sheet: the lead, its level, the sheet and skill
    hashes, and the objective the week is held to. The spec itself is never changed, so
    Krish's Clear still binds exactly the spec. Refused with every reason when the sheet is
    invalid, has no lead, or the spec does not name the objective the lead is measured by."""
    errors = validate(sheet, adapter, state, methods, root)
    if not errors and sheet.get('lead') is None:
        errors.append('the sheet has no lead (the blind passes disagreed); show Krish the sheet, do not seed the week')
    if errors:
        raise ValueError('the insight sheet is refused: ' + '; '.join(errors))
    idea = next(i for i in sheet['ideas'] if i['id'] == sheet['lead'])
    objective = MEASURED_BY.get(idea['idea_level'])
    named = {o.get('key') for o in campaign.get('objectives') or [] if isinstance(o, dict)}
    if objective and objective not in named:
        raise ValueError(f'the lead {idea["id"]} is a {idea["idea_level"]} idea; the spec must name the objective '
                         f'{objective} it is measured by')
    return {'sheet_sha256': sheet['sheet_sha256'], 'harness_skill_sha': sheet['harness_skill_sha'],
            'lead': idea['id'], 'idea_level': idea['idea_level'], 'claim': idea['claim'],
            'objective_key': objective}
