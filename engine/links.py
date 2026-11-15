"""The link audit: does a tracked Full Time link still carry its tags when it lands, and
what does a fan's share of it show? Read-only, Python standard library only.

Adopted from the Claude Ads review of 15 November 2026 (docs/CLAUDE-ADS.md): a tag in a
caption is not proof of measurement, so follow the link to the page it lands on. Every
check ends pass, fail, unknown or not_applicable. Unknown is a real answer (the page
could not be read) and is never counted as a pass.

The checks, for each link:
- https: the link is https.
- on_full_time: the link and every redirect stay on fulltime.fm or www.fulltime.fm. A
  redirect anywhere else is a fail and is never fetched.
- lands: the last hop answers 200.
- tags_survive: every utm_* tag, the share token s, drop and pundit the link carries reach
  the landing URL with the same values. A redirect that drops one loses the attribution.
- preview: the landing page names an Open Graph title and image, the card a share shows.
- preview_keeps_show: for a link to one show (it carries drop), the page's og:url, or its
  canonical link when og:url is absent, keeps that drop and AI Pundit. Otherwise a fan's
  share shows the site card, not this AI Pundit's show (briefs/2026-10-27-share-attribution.md,
  item 6).

Safety: GET only, no cookies, no scripts run (so no analytics event fires), at most
MAX_HOPS redirects, at most LIMIT bytes read per page. A share token's value never appears
in the output. Nothing here posts, sends, schedules or spends.
"""
from html.parser import HTMLParser
import http.client
import re
import urllib.error
import urllib.parse
import urllib.request

HOSTS = ('fulltime.fm', 'www.fulltime.fm')
KEPT = ('s', 'drop', 'pundit')   # with every utm_* key the link carries
EDITION = ('drop', 'pundit')
SECRET = ('s',)
RESULTS = ('pass', 'fail', 'unknown', 'not_applicable')
CHECKS = ('https', 'on_full_time', 'lands', 'tags_survive', 'preview', 'preview_keeps_show')
MAX_HOPS = 5
LIMIT = 512 * 1024
TIMEOUT = 20
REDIRECTS = (301, 302, 303, 307, 308)
USER_AGENT = 'growth-fulltime link audit (+https://github.com/krishanraja/growth-fulltime)'
TRAILING = '.,;:!?'
INTERNAL = ('site', 'other')   # notes for Krish, where a bare fulltime.fm is not a link anyone clicks
# A backslash, a space or a control character in a URL: browsers read some of them as a path
# separator or strip them, so the host Python parses may not be the host a fan reaches.
UNSAFE = re.compile(r'[\\\x00-\x20\x7f]')


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Hand every redirect back to the audit, so it checks each hop before going on."""
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def fetch(url, timeout=TIMEOUT):
    """(status, location, content_type, body) for one GET, never following a redirect."""
    opener = urllib.request.build_opener(_NoRedirect)
    request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT, 'Accept': 'text/html'}, method='GET')
    try:
        with opener.open(request, timeout=timeout) as response:
            return (response.status, response.headers.get('Location'), response.headers.get('Content-Type') or '',
                    response.read(LIMIT))
    except urllib.error.HTTPError as error:
        try:
            body = error.read(LIMIT)
        except OSError:
            body = b''
        return error.code, error.headers.get('Location'), error.headers.get('Content-Type') or '', body


def _redacted(text):
    pairs = urllib.parse.parse_qsl(text, keep_blank_values=True)
    if not any(key in SECRET for key, _ in pairs):
        return text
    return urllib.parse.urlencode([(k, 'REDACTED' if k in SECRET else v) for k, v in pairs], safe='()')


def shown(url, secrets=()):
    """The URL as the audit prints it: a share token's value replaced wherever it appears (its
    query, its fragment, or a path the site moved it into), everything else as it is."""
    try:
        parts = urllib.parse.urlsplit(url)
        url = urllib.parse.urlunsplit(parts._replace(query=_redacted(parts.query),
                                                     fragment=_redacted(parts.fragment)))
    except ValueError:
        pass
    for secret in secrets:
        if len(secret) >= 4:
            url = url.replace(secret, 'REDACTED').replace(urllib.parse.quote(secret, safe=''), 'REDACTED')
    return url


def _params(url):
    pairs = urllib.parse.parse_qsl(urllib.parse.urlsplit(url).query, keep_blank_values=True)
    out = {}
    for key, value in pairs:
        out.setdefault(key, []).append(value)
    return out


def _on_full_time(url):
    """True only for a plain https URL on fulltime.fm or www.fulltime.fm: no userinfo, no port
    but 443, and no character a browser might read differently from Python."""
    if not isinstance(url, str) or UNSAFE.search(url):
        return False
    try:
        parts = urllib.parse.urlsplit(url)
        return (parts.scheme == 'https' and '@' not in parts.netloc
                and (parts.hostname or '').lower() in HOSTS and parts.port in (None, 443))
    except ValueError:   # an invalid port or bracketed host
        return False


def _carried(url):
    return {k: v for k, v in _params(url).items() if k.startswith('utm_') or k in KEPT}


class _Head(HTMLParser):
    """The share-preview tags in a page: og:* and twitter:* meta tags and the canonical link."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta, self.canonical = {}, None

    def handle_starttag(self, tag, attrs):
        attrs = {k.lower(): (v or '') for k, v in attrs}
        if tag == 'meta':
            key = (attrs.get('property') or attrs.get('name') or '').lower()
            if key.startswith(('og:', 'twitter:')) and key not in self.meta:
                self.meta[key] = attrs.get('content', '').strip()
        elif tag == 'link' and 'canonical' in attrs.get('rel', '').lower().split() and self.canonical is None:
            self.canonical = attrs.get('href', '').strip()


def head(body, content_type=''):
    """{'meta': {...}, 'canonical': ...} read from an HTML body, or None when it is not HTML."""
    if 'html' not in content_type.lower() and b'<html' not in body[:4096].lower():
        return None
    parser = _Head()
    parser.feed(body.decode('utf-8', errors='replace'))
    return {'meta': parser.meta, 'canonical': parser.canonical}


def _check(result, why):
    assert result in RESULTS
    return {'result': result, 'why': why}


def audit_one(url, opener=fetch):
    """The audit of one link, following its redirects hop by hop. `opener(url)` returns
    (status, location, content_type, body); tests pass a stand-in, so they never touch the network."""
    checks = {}
    hops = []
    url = url.strip().rstrip(TRAILING)
    carried = _carried(url)
    secrets = tuple(v for key in SECRET for v in carried.get(key, []))
    if urllib.parse.urlsplit(url).scheme != 'https':
        checks['https'] = _check('fail', 'the link is not https (paste the exact link growth.py link prints)')
    else:
        checks['https'] = _check('pass', 'https')
    if not _on_full_time(url):
        checks['on_full_time'] = _check('fail', 'the link is not on fulltime.fm over https, so it was not fetched')
        for name in CHECKS[2:]:
            checks[name] = _check('unknown', 'not fetched')
        return _finish(url, hops, checks, secrets)
    current, page, outcome = url, None, None
    for _ in range(MAX_HOPS + 1):
        try:
            status, location, content_type, body = opener(current)
        except (OSError, ValueError, http.client.HTTPException) as error:
            # URLError, timeouts and refused connections are OSError; a broken body is HTTPException
            hops.append({'url': shown(current, secrets), 'status': None, 'error': type(error).__name__})
            checks['on_full_time'] = _check('unknown', f'{len(hops) - 1} hop(s) on Full Time, then the chain '
                                                       'could not be read to its end')
            outcome = _check('unknown', f'the page could not be read ({type(error).__name__})')
            break
        hops.append({'url': shown(current, secrets), 'status': status})
        if status in REDIRECTS and location:
            try:
                following = '' if UNSAFE.search(location) else urllib.parse.urljoin(current, location)
            except ValueError:
                following = ''
            if not _on_full_time(following):
                checks['on_full_time'] = _check('fail', f'hop {len(hops)} redirects off Full Time, or to a URL a '
                                                        f'browser may read differently ({shown(location, secrets)!r}); '
                                                        'it was not fetched')
                hops.append({'url': shown(location, secrets), 'status': 'not fetched'})
                outcome = _check('fail', 'it never landed on a Full Time page')
                break
            current = following
            continue
        if status == 200:
            page = head(body, content_type)
            outcome = _check('pass', 'answered 200')
        else:
            outcome = _check('fail', f'the last hop answered {status}')
        break
    else:
        checks['on_full_time'] = _check('unknown', f'more than {MAX_HOPS} redirects: the end was not seen')
        outcome = _check('fail', f'more than {MAX_HOPS} redirects')
    checks.setdefault('on_full_time', _check('pass', f'{len(hops)} hop(s), all on Full Time'))
    checks['lands'] = outcome
    landed = outcome['result'] == 'pass'
    if not carried:
        checks['tags_survive'] = _check('not_applicable', 'the link carries no utm_* tag, share token, drop or pundit')
    elif not landed:
        checks['tags_survive'] = _check(checks['lands']['result'] if checks['lands']['result'] == 'unknown' else 'fail',
                                        'it did not land, so its tags reach nothing')
    else:
        final = _params(current)
        lost = sorted(k for k, v in carried.items() if final.get(k) != v)
        checks['tags_survive'] = (_check('fail', 'lost or changed on the way: ' + ', '.join(lost)) if lost else
                                  _check('pass', 'kept: ' + ', '.join(sorted(carried))))
    if not landed:
        checks['preview'] = _check(checks['lands']['result'] if checks['lands']['result'] == 'unknown' else 'fail',
                                   'no page to read')
        checks['preview_keeps_show'] = (_check('not_applicable', 'the link names no show') if 'drop' not in carried
                                        else _check(checks['preview']['result'], 'no page to read'))
        return _finish(url, hops, checks, secrets)
    if page is None:
        checks['preview'] = _check('unknown', 'the page is not HTML, so its share card could not be read')
        checks['preview_keeps_show'] = _check('not_applicable' if 'drop' not in carried else 'unknown',
                                              'the link names no show' if 'drop' not in carried else 'not HTML')
        return _finish(url, hops, checks, secrets)
    meta = page['meta']
    missing = [k for k in ('og:title', 'og:image') if not meta.get(k)]
    checks['preview'] = (_check('fail', 'no ' + ' or '.join(missing) + ', so a share shows a bare link') if missing
                         else _check('pass', f'og:title "{meta["og:title"][:120]}" with an image'))
    if 'drop' not in carried:
        checks['preview_keeps_show'] = _check('not_applicable', 'the link names no show')
    else:
        pointer = meta.get('og:url') or page['canonical']
        named = 'og:url' if meta.get('og:url') else 'canonical'
        if not pointer:
            checks['preview_keeps_show'] = _check('pass', 'no og:url or canonical: a share card is read from the link itself')
        else:
            try:
                target = _params(urllib.parse.urljoin(current, pointer))
            except ValueError:
                target = {}
            lost = [k for k in EDITION if k in carried and target.get(k) != carried[k]]
            checks['preview_keeps_show'] = (
                _check('fail', f'{named} is {shown(pointer, secrets)}, which drops {", ".join(lost)}: a fan\'s share shows the '
                               'site card, not this AI Pundit\'s show (share brief, item 6)') if lost
                else _check('pass', f'{named} keeps the show\'s drop and AI Pundit'))
    return _finish(url, hops, checks, secrets)


def _finish(url, hops, checks, secrets=()):
    results = [c['result'] for c in checks.values()]
    verdict = 'fail' if 'fail' in results else ('unknown' if 'unknown' in results else 'pass')
    return {'url': shown(url, secrets), 'verdict': verdict, 'checks': {k: checks[k] for k in CHECKS}, 'hops': hops}


def links_in(pack, own_link):
    """Every Full Time link in a pack: each item's target_url and the links in its text, in order, once.
    `own_link` is growth.OWN_LINK, the pattern the pack check uses. As in the pack check, a bare
    fulltime.fm in a note for Krish (platform site or other) is not a link anyone clicks."""
    found = []
    for item in pack.get('items') or []:
        if not isinstance(item, dict):
            continue
        candidates = [item.get('target_url')] if isinstance(item.get('target_url'), str) else []
        if isinstance(item.get('text'), str):
            internal = str(item.get('platform', '')).lower() in INTERNAL
            candidates += [x for x in own_link.findall(item['text'])
                           if not (internal and not re.match(r'https?://', x, re.I))]
        for raw in candidates:
            link = raw.strip().rstrip(TRAILING)
            if link and link not in found:
                found.append(link)
    return found


def audit(urls, opener=fetch):
    """The audit of every link, with a summary: each result's count across all checks, and coverage,
    the applicable checks with a known result (Claude Ads' evidence coverage)."""
    if not urls:
        raise ValueError('give at least one link, or a pack with --pack')
    rows = [audit_one(url, opener) for url in urls]
    counts = {r: 0 for r in RESULTS}
    for row in rows:
        for check in row['checks'].values():
            counts[check['result']] += 1
    applicable = counts['pass'] + counts['fail'] + counts['unknown']
    verdicts = [row['verdict'] for row in rows]
    verdict = 'fail' if 'fail' in verdicts else ('unknown' if 'unknown' in verdicts else 'pass')
    return {'verdict': verdict, 'counts': counts,
            'coverage': f'{counts["pass"] + counts["fail"]} of {applicable} applicable checks known',
            'links': rows, 'read_only': True, 'scripts_run': False}
