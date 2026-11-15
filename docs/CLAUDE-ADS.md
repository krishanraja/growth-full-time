# Claude Ads review (15 November 2026)

Krish asked which advertising audit and optimisation capabilities in Claude Ads
genuinely improve Full Time's growth system, for channels it uses or has an approved
reason to test, with external accounts kept read-only or draft-only.

Source: [AgriciDaniel/claude-ads](https://github.com/AgriciDaniel/claude-ads) at
commit `fc3908e` (17 October 2026), MIT licence. It was read, not installed, and no
code was copied: the parts adopted are rewritten here in the standard library.

## The channels it was judged against

- **In use, once a format is ready:** organic TikTok, Reels and Shorts from one
  vertical master, with derived cards elsewhere (AGENTS.md, rulings 1 and 2). Krish
  posts by hand in Buffer (ruling 3). No ad account exists.
- **Proposed, not approved:** one paid test, ruling D5 in `rulings.json` (up to £300,
  boosting the best organic clip on TikTok Spark Ads and Meta, after D7). Paid ads
  are not banned (Ruling, Krish, 2026-11-15: "Full Time does not ban paid ads"), so
  since 15 November `ads` is gated by D5, D7, RELEASE and the rail, not refused, and
  D5 is an ask on his list once the engine is released. Full-time's own doctrine
  keeps paid promotion off for the pilot beta (`docs/22-vision-and-beta.md`, "The
  pilot beta"); the RELEASE hold on every paid draft keeps it off until the product's
  release decision.

## Adopted

| Claude Ads idea | Built here | Why it moves the North Star |
|---|---|---|
| A tag is not proof of measurement: trace it to where it lands (`conversion-tracking.md`, `ads-landing`) | `engine/links.py`, `growth.py links audit URL... \| --pack FILE` | A redirect that drops `utm_content` or the share token `s` makes a shared take uncountable. It also checks the card a fan's share shows |
| Sample size and duration from declared assumptions, disclosed as approximate (`ads-test`) | `engine.learning.plan()`, `growth.py learning plan` | Says before a test starts whether it can reach the What-Works bar in time, so no matchweeks go on a test that cannot be read |
| Experiment economics, never hiding a division by zero (`ads-math`) | `engine.learning.cost_per_event()` and `spend_plan()`, `growth.py learning cost` | Cost per new listener with the count's interval, for credits now and for the D5 budget if he approves it |
| Every check ends pass, fail, unknown or not applicable, with evidence coverage (`scoring-system.md`) | The link audit's results and its coverage line | Unknown stays unknown, as MEASUREMENT.md already requires |

The first live run (15 November, read-only, no scripts run) on the published Tottenham v
Coventry show (AI Pundit `zen`): every tag and the drop and AI Pundit survive, including
the 308 redirect from www to fulltime.fm. Both links fail `preview_keeps_show`: the page's
`og:url` and canonical are `https://fulltime.fm/`, so a fan's share of any show
shows the site card, not that AI Pundit's show. That is item 6 of the share brief
(`briefs/2026-10-27-share-attribution.md`), a product change.

## Already here, often stricter

The comparability gate (never add windows, Google Analytics never becomes a listener),
no alerts on trivial denominators (20 events per arm, z of 2), pre-registration and no
peeking (frozen fields in the learning register), missing never written as zero, and
draft-only with a human doing the go-live (ruling 3). Nothing changed.

## Rejected

- **Installing the plugin.** It adds over 30 skills across 12 paid platforms that
  trigger on everyday words, managed Python 3.11 or 3.12 dependencies, Playwright and
  WeasyPrint. This engine is standard-library Python 3.9 or later, and nothing in the
  plugin works on an organic channel.
- **Platform audits** for Google, Microsoft, Apple, Amazon, LinkedIn, Pinterest,
  Reddit, Snapchat, X and YouTube Ads: no account and no approved test.
- **TikTok and Meta audits:** the D5 test's channels, so deferred until D5 is
  approved (below), not built ahead of it.
- **Planning, budgeting, launch, optimisation, ad creation, image generation,
  brand DNA and competitor ad-library skills:** each plans or changes paid campaigns,
  or makes or researches paid creative. The creative system, the prepaid credits and
  Krish's own hand cover what Full Time does.
- **The landing-page analyser:** a browser audit for lead-generation pages (forms,
  trust badges, Core Web Vitals). The checks that matter for a share link are in the
  link audit without a browser.
- **Creative fatigue diagnostics:** they need paid delivery over time. Each organic
  take is reviewed at 24 hours, 72 hours and 7 days (GET-GOING, Step 7).
- **The cockpit, release tooling and model evals:** Claude Ads' own product machinery.

## If Krish approves D5 (the paid test)

In this order, each read-only or draft-only until his approval of the exact spend:

1. D7 is closed first: an ad pixel needs a consent banner
   (`knowledge/full-time-1000-users-playbook.md`, P8).
2. `growth.py learning cost --budget-gbp 300 --cost-gbp LOW HIGH` says whether the
   budget can reach 20 new listeners at all; afterwards `--spend-gbp` and `--events`
   give the cost per new listener with its band.
3. The ad's own link carries an `AD_` creative ID (`growth.tracked` tags it
   `utm_source=paid`, `utm_medium=paid`), so paid arrivals stay apart from brand-post
   and share arrivals. A Spark Ad boosts the organic post itself, so any learning that
   uses that post is marked overlapping while the boost runs.
4. `growth.py links audit` on the ad's link before it goes to Krish.
5. Then, if wanted: the Claude Ads TikTok and Meta audit references, read-only, at a
   pinned and reviewed commit, against an export of that one campaign.

The Control Center objective `marketing_cash_gbp` has a target of 0; a paid test
would need Krish to change it there.
