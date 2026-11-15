"""The read-only link audit (engine/links.py). Every page is a stand-in: no network,
synthetic links and a synthetic share token only."""
import json
import unittest

import growth
from engine import links

DROP = 'aaaaaaaa-0000-4000-8000-000000000001'
CID = 'TT_CLASH_CLIP_C01_H01_V1_20261115'
TOKEN = 'synthetictoken' + '42'
SHOW = growth.tracked(f'https://fulltime.fm/?drop={DROP}&pundit=zen', CID)


def page(og_url=None, title='Full Time', image='https://fulltime.fm/og-card.png', canonical=None):
    tags = ''
    if title:
        tags += f'<meta property="og:title" content="{title}"/>'
    if image:
        tags += f'<meta property="og:image" content="{image}"/>'
    if og_url:
        tags += f'<meta property="og:url" content="{og_url}"/>'
    if canonical:
        tags += f'<link rel="canonical" href="{canonical}"/>'
    return f'<!DOCTYPE html><html><head>{tags}</head><body></body></html>'.encode()


class Site:
    """A stand-in for fulltime.fm: answers by URL, records every URL it was asked for."""
    def __init__(self, answers, default=None):
        self.answers, self.default, self.asked = answers, default, []

    def __call__(self, url):
        self.asked.append(url)
        answer = self.answers.get(url, self.default)
        if isinstance(answer, Exception):
            raise answer
        if answer is None:
            return 404, None, 'text/html', b''
        return answer


def ok(body=None):
    return 200, None, 'text/html; charset=utf-8', body if body is not None else page()


class Redirects(unittest.TestCase):
    def test_tags_survive_a_redirect_that_keeps_the_query(self):
        www = SHOW.replace('https://fulltime.fm', 'https://www.fulltime.fm')
        site = Site({www: (308, SHOW, 'text/plain', b''), SHOW: ok()})
        row = links.audit_one(www, site)
        self.assertEqual(row['checks']['tags_survive']['result'], 'pass')
        self.assertEqual([h['status'] for h in row['hops']], [308, 200])

    def test_a_redirect_that_drops_the_query_loses_the_tags(self):
        site = Site({SHOW: (301, 'https://fulltime.fm/', 'text/plain', b''), 'https://fulltime.fm/': ok()})
        row = links.audit_one(SHOW, site)
        self.assertEqual(row['checks']['tags_survive']['result'], 'fail')
        for key in ('utm_content', 'drop', 'pundit'):
            self.assertIn(key, row['checks']['tags_survive']['why'])
        self.assertEqual(row['verdict'], 'fail')

    def test_a_redirect_off_full_time_is_never_fetched(self):
        site = Site({SHOW: (302, 'https://elsewhere.example/landing', 'text/plain', b'')}, default=ok())
        row = links.audit_one(SHOW, site)
        self.assertEqual(row['checks']['on_full_time']['result'], 'fail')
        self.assertEqual(site.asked, [SHOW])
        self.assertEqual(row['checks']['lands']['result'], 'fail')

    def test_a_link_off_full_time_or_without_https_is_never_fetched(self):
        for url in ('https://elsewhere.example/?drop=x', SHOW.replace('https://', 'http://'),
                    'https://fulltime.fm.evil.example/', 'https://user@fulltime.fm/', 'https://fulltime.fm:8443/'):
            with self.subTest(url=url):
                site = Site({}, default=ok())
                row = links.audit_one(url, site)
                self.assertEqual(site.asked, [])
                self.assertEqual(row['verdict'], 'fail')

    def test_endless_redirects_stop(self):
        site = Site({}, default=(307, SHOW, 'text/plain', b''))
        row = links.audit_one(SHOW, site)
        self.assertEqual(len(site.asked), links.MAX_HOPS + 1)
        self.assertEqual(row['checks']['lands']['result'], 'fail')


class Landing(unittest.TestCase):
    def test_a_page_that_cannot_be_read_is_unknown_never_a_pass(self):
        row = links.audit_one(SHOW, Site({SHOW: OSError('timed out')}))
        self.assertEqual(row['checks']['lands']['result'], 'unknown')
        self.assertEqual(row['verdict'], 'unknown')
        self.assertNotIn('pass', [row['checks'][k]['result'] for k in ('lands', 'tags_survive', 'preview')])

    def test_a_missing_page_fails(self):
        row = links.audit_one(SHOW, Site({}))
        self.assertEqual((row['checks']['lands']['result'], row['verdict']), ('fail', 'fail'))

    def test_a_page_without_an_image_has_no_share_card(self):
        row = links.audit_one(SHOW, Site({SHOW: ok(page(image=None))}))
        self.assertEqual(row['checks']['preview']['result'], 'fail')
        self.assertIn('og:image', row['checks']['preview']['why'])

    def test_a_non_html_answer_leaves_the_card_unknown(self):
        row = links.audit_one(SHOW, Site({SHOW: (200, None, 'application/json', b'{}')}))
        self.assertEqual(row['checks']['preview']['result'], 'unknown')


class SharePreview(unittest.TestCase):
    def test_og_url_pointing_home_fails_a_show_link(self):
        row = links.audit_one(SHOW, Site({SHOW: ok(page(og_url='https://fulltime.fm/'))}))
        check = row['checks']['preview_keeps_show']
        self.assertEqual(check['result'], 'fail')
        self.assertIn('site card', check['why'])

    def test_og_url_that_keeps_the_show_passes(self):
        own = f'https://fulltime.fm/?drop={DROP}&amp;pundit=zen'
        row = links.audit_one(SHOW, Site({SHOW: ok(page(og_url=own))}))
        self.assertEqual(row['checks']['preview_keeps_show']['result'], 'pass')
        self.assertEqual(row['verdict'], 'pass')

    def test_the_canonical_counts_when_there_is_no_og_url(self):
        row = links.audit_one(SHOW, Site({SHOW: ok(page(canonical='https://fulltime.fm/'))}))
        self.assertEqual(row['checks']['preview_keeps_show']['result'], 'fail')
        self.assertIn('canonical', row['checks']['preview_keeps_show']['why'])

    def test_a_link_that_names_no_show_is_not_applicable(self):
        privacy = growth.tracked('https://fulltime.fm/legal/privacy', CID)
        row = links.audit_one(privacy, Site({privacy: ok(page(og_url='https://fulltime.fm/'))}))
        self.assertEqual(row['checks']['preview_keeps_show']['result'], 'not_applicable')
        self.assertEqual(row['verdict'], 'pass')

    def test_a_share_tokens_value_never_appears(self):
        shared = f'https://fulltime.fm/?drop={DROP}&pundit=zen&s={TOKEN}'
        result = links.audit([shared], Site({shared: ok(page(og_url='https://fulltime.fm/'))}))
        text = json.dumps(result)
        self.assertNotIn(TOKEN, text)
        self.assertIn('s=REDACTED', text)
        self.assertIn('s,', result['links'][0]['checks']['tags_survive']['why'] + ',')


class Packs(unittest.TestCase):
    def test_every_full_time_link_in_a_pack_once_without_trailing_punctuation(self):
        pack = {'items': [{'platform': 'tiktok', 'target_url': SHOW, 'text': f'Hear the Zen take: {SHOW}.'},
                          {'platform': 'youtube', 'text': 'No link here.'},
                          {'platform': 'x', 'text': 'Two: https://fulltime.fm/?drop=b&pundit=zen, and more'}]}
        self.assertEqual(links.links_in(pack, growth.OWN_LINK), [SHOW, 'https://fulltime.fm/?drop=b&pundit=zen'])

    def test_the_summary_counts_every_check_and_its_coverage(self):
        site = Site({SHOW: ok(page(og_url='https://fulltime.fm/'))})
        result = links.audit([SHOW], site)
        self.assertEqual(result['counts'], {'pass': 5, 'fail': 1, 'unknown': 0, 'not_applicable': 0})
        self.assertEqual(result['coverage'], '6 of 6 applicable checks known')
        self.assertEqual((result['verdict'], result['read_only'], result['scripts_run']), ('fail', True, False))
        with self.assertRaises(ValueError):
            links.audit([])



class ReviewRegressions(unittest.TestCase):
    """Findings of the independent review of 15 November 2026, each kept as a test."""

    def test_a_backslash_redirect_is_off_full_time_and_never_fetched(self):
        site = Site({SHOW: (302, '/\\elsewhere.example/?drop=d&pundit=zen', 'text/plain', b'')}, default=ok())
        row = links.audit_one(SHOW, site)
        self.assertEqual((row['checks']['on_full_time']['result'], row['verdict']), ('fail', 'fail'))
        self.assertEqual(site.asked, [SHOW])

    def test_a_malformed_redirect_fails_without_crashing(self):
        for location in ('https://fulltime.fm:99999/', 'https://[::1/', 'https://:pw@fulltime.fm/', '/x\tpath'):
            with self.subTest(location=location):
                site = Site({SHOW: (301, location, 'text/plain', b'')}, default=ok())
                row = links.audit_one(SHOW, site)
                self.assertEqual(row['checks']['on_full_time']['result'], 'fail')
                self.assertEqual(site.asked, [SHOW])

    def test_userinfo_with_only_a_password_is_never_fetched(self):
        site = Site({}, default=ok())
        self.assertEqual(links.audit_one('https://:pw@fulltime.fm/?drop=d', site)['verdict'], 'fail')
        self.assertEqual(site.asked, [])

    def test_a_chain_not_read_to_its_end_is_unknown_not_on_full_time(self):
        import http.client
        for error in (OSError('reset'), http.client.IncompleteRead(b'')):
            with self.subTest(error=type(error).__name__):
                row = links.audit_one(SHOW, Site({SHOW: error}))
                self.assertEqual(row['checks']['on_full_time']['result'], 'unknown')
                self.assertEqual(row['verdict'], 'unknown')
        endless = links.audit_one(SHOW, Site({}, default=(307, SHOW, 'text/plain', b'')))
        self.assertEqual(endless['checks']['on_full_time']['result'], 'unknown')

    def test_every_utm_tag_is_checked(self):
        tagged = SHOW + '&utm_term=derby'
        site = Site({tagged: (301, SHOW, 'text/plain', b''), SHOW: ok()})
        row = links.audit_one(tagged, site)
        self.assertEqual(row['checks']['tags_survive']['result'], 'fail')
        self.assertIn('utm_term', row['checks']['tags_survive']['why'])

    def test_a_share_token_moved_into_a_path_or_fragment_is_never_printed(self):
        shared = f'https://fulltime.fm/?drop={DROP}&pundit=zen&s={TOKEN}'
        moved = f'https://fulltime.fm/share/{TOKEN}#s={TOKEN}'
        result = links.audit([shared], Site({shared: (302, moved, 'text/plain', b''), moved.split('#')[0]: ok()},
                                            default=ok()))
        self.assertNotIn(TOKEN, json.dumps(result))

    def test_a_bare_mention_in_a_note_for_krish_is_not_audited(self):
        pack = {'items': [{'platform': 'other', 'text': 'Check fulltime.fm before Saturday.'},
                          {'platform': 'tiktok', 'text': 'Hear it at fulltime.fm/today'}]}
        self.assertEqual(links.links_in(pack, growth.OWN_LINK), ['fulltime.fm/today'])


if __name__ == '__main__':
    unittest.main()
