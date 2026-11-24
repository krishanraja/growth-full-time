# History log

Newest first. Entries are written by the closeout fold (`python3 growth.py closeout fold`, engine/closeout.py),
by the docs steward (`krishanraja/ai-harness`, `docs/steward/RUNBOOK.md`) and by people doing the same job by
hand. Nothing in this file describes current behaviour; `NOW.md` and `README.md` do. Text moved here from
`NOW.md` keeps its wording verbatim; only its relative links are re-pointed to work from here.

## 2026-11-24

Moved verbatim from `NOW.md` (closeout fold, to keep NOW.md inside the audit's limits).

From "What changed recently":

- 2026-10-23 **The North Star now has a number, a weekly ladder and an urgency rating.** Ruling (Krish, 2026-10-23): every repository chases one aggressive number on a weekly ladder, and urgency U1 to U5 sets how hard it pushes. The number is in `docs/NORTH_STAR.md`; contract: ai-harness `contract/north-star-metric.md`.

From "Where it is right now":

- The fleet audit's repairs landed. The docs say the daily credits task exists and is switched off while held. NOW.md and MEASUREMENT.md name the one weekly aggregate full-time must export for the North Star to be measured. GET-GOING.md has a release checklist (re-copy the protocol, read `ai_answers_detail` first, switch the credits task back on). A hand-started run proved the held report live in Control Center: `held`, 1.20.0, no proposals, one NOT_READY hold. (2026-11-14)
- Full Time's AI answers are AEO-Engine's, the one AI-answers specialist (Ruling, Krish, 2026-11-12): AEO already researches Full Time every fortnight, and the runner reads its standing from the directive into one line (protocol 1.22.0, engine/ai_answers.py). The protocol copy in docs/control-center/ is Control Center's at 36df34bc (protocol 1.22.0). (2026-11-13)
- The protocol copy in docs/control-center/ is Control Center's at 212379e1 (1.21.0, the schemas unchanged): its voice_check row lists the 16 channels Control Center accepts, and it says a number objective's target comes from the repository's north-star block; Control Center reads no number objective for this engine (only Legibility, Mindmake, Heartside and Make Your Mind Up have one), so its registered objectives keep their registry targets. The code still speaks 1.20.0 and the engine is still held. (2026-11-12)
- The docs match the code and the live state, the engine's obsessions quote only Krish's own words, a repeated ack with a new line now updates Control Center (protocol 1.21.0), and closeout notes fold into NOW.md on every merge to main (engine/closeout.py). (2026-11-12)
- The code speaks Control Center protocol 1.20.0: a run reads Krish's instruction, acks it by id and reports its priorities, obsessions and next steps (`engine/engine_state.py`). The state reached Control Center first in the held run of 14 November; Krish has given this engine no instruction. (2026-11-14)

## 2026-11-15

Engine v2 merged onto main, keeping main's Control Center report (Ruling, Krish, 2026-11-15). The branch's
own history lines, verbatim:

- 2026-10-27: engine v2 built, reviewed twice and fixed; Krish's daily actions in every report; the social kit "The Switch, revision 1" approved ("I like it. Looks good."). See `HANDOVER-2026-10-27-ENGINE-V2.md`.
- 2026-10-27: engine v2 approved ("approved, do it all"); nine rulings recorded; the Drive library `Growth Build` organised with START-HERE and INDEX. See `docs/ENGINE-V2.md`.
- 2026-10-27: the private two-ad creative handoff archived to Drive with exact hashes (`HANDOVER-2026-10-27-CREATIVES.md`).
- 2026-10-26: versioned creative standards, regression gates and the product personality bridge (PRs 10 to 12).
- 2026-10-23: the North Star got a number, a weekly ladder and urgency U1 to U5.
- 2026-10-22: human listening standard; this week's media-credit allocation brief.
- 2026-10-19: Control Center protocol adopted (live from the first run); autonomy ruling; copywriting corpus absorbed.
- 2026-10-18: North Star set.
- 2026-10-16 to 17: the engine built and completed with zero new marketing cash.

## 2026-11-14

Moved verbatim from `NOW.md` (closeout fold, to keep NOW.md inside the audit's limits).

From "Where it is right now":

- The promotion rail is on HOLD: the four matches on fulltime.fm each have one AI Pundit of six, the newest from 19 October (`state/FULLTIME-NOW.md`, read hourly). A push needs a match with four. (2026-11-12)

## 2026-11-14

Moved verbatim from `NOW.md` (closeout fold, to keep NOW.md inside the audit's limits).

From "Where it is right now":

- Rulings D1 to D7 are all pending, and full-time's `docs/12-roadmap.md` records no release decision (`rulings.json`, `state/FULLTIME-NOW.md`). (2026-11-12)

## 2026-11-14

Moved verbatim from `NOW.md` (closeout fold, to keep NOW.md inside the audit's limits).

From "Where it is right now":

- The credits share is read and guarded (`engine/credits.py`) but nothing spends it: the engine is held. The daily credits task in docs/CREDITS-SESSION.md exists on claude.ai and is switched off while held (since 2026-11-14); it is switched back on at release, never recreated. (2026-11-14)

## 2026-11-14

Moved verbatim from `NOW.md` (closeout fold, to keep NOW.md inside the audit's limits).

From "Where it is right now":

- Creative: Liverpool v8 is a listening candidate Krish has not judged, and the Arsenal video is still rejected; neither ad is ready to post. The private package is in the Growth Build Drive folder named in HANDOVER-2026-10-27-CREATIVES.md. (2026-10-27)

## 2026-11-12

Moved verbatim from `NOW.md` (the 12 November docs audit, when NOW.md was rewritten to match the code and
live state), and the six closeout notes that had waited in `now-notes/` since 29 October with no fold to
write them in, each verbatim. From now on the fold job in `.github/workflows/check.yml` writes each note
into NOW.md (`engine/closeout.py`).

From "Where it is right now (as of 2026-10-27)":

<!-- north-star-state {"week_of": "2026-10-26", "week_target": 5, "current": null, "current_as_of": "2026-10-27", "current_source": "No fresh cohort measurement available; prior 2026-10-23 value is historical", "urgency": 4, "urgency_reason": "current number unmeasured"} --> **North Star number: U4, unmeasured.** New listeners this week who arrived through a fan's shared link or clip: unknown, against 5 this week, on the way to 1,250 by 25 January 2027. The previous 0 was a 23 October observation, not a measurement of this week's attribution.

Lifecycle: building. The detail is in `README.md`.

The offline [creative system](../../creative-system/README.md) now pins independent
character and shared-style modules, exact input hashes and owner review evidence.
It preserves private creative history under ignored `local/creative-system/` and
starts with `python3 growth.py standards startup`. Creative acceptance and
technical success are separate; no new generation, publication or product
change is authorised by loading a baseline. A fresh product sync still reports
the minimum-four-pundit rail HOLD.

The product now owns the reusable six-pundit core in `krishanraja/full-time`;
growth imports and pins a committed export rather than owning duplicate identities.
Ad performance, sofa cast, visual direction and exact audio locks stay here.
The baseline and bridge are merged in PRs #10 and #11. Product PR #99 is merged;
the active private release pins its exact core from product commit `43c4ae2`.
The original audio locks and four owner video rejections survive this ownership
migration; it claims no new creative approval. The complete private continuation
package now lives in the [canonical Growth Build Drive folder](https://drive.google.com/drive/folders/1Pn_ibUcfpcyWzi4w1ryDMZMF-8m1gT_M).
Read [the 27 October creative handover](../../HANDOVER-2026-10-27-CREATIVES.md) first.
It contains the exact package hashes, restore route, owner corrections and next
review target. Liverpool v8 is a listening candidate; neither ad is ready to post.

Local proof: 131 self-checks, 129 unit/integration tests including 46 creative
tests, and repository verification passed. Actual session assets remain private.
The local operational run refused to proceed because existing growth history
was absent; no live report was sent or fresh operational ledger created.

From "What changed recently":

- 2026-10-27: archived the full private two-ad session and creative baseline to
  Drive, verified local rebuild and Drive file identity/size readback, and set a
  portable start-here path. The Liverpool ending, accents and TV music remain
  subject to owner listening. See [current handover](../../HANDOVER-2026-10-27-CREATIVES.md).

- 2026-10-26: implemented versioned creative standards, isolated composition,
  scope checks, improvement/regression gates, exact owner promotion and verified
  private bundle recovery. See [handover](../../HANDOVER-2026-10-26.md).

- 2026-10-23 **The North Star now has a number, a weekly ladder and an urgency rating.** Ruling (Krish, 2026-10-23): every repository chases one aggressive number on a weekly ladder, and urgency U1 to U5 sets how hard it pushes. The number is in `docs/NORTH_STAR.md`; contract: ai-harness `contract/north-star-metric.md`.

From "What is next and what is waiting on Krish":

- Review the full Liverpool v8 mix with Krish, correct only what the listening
  warrants, then get both existing concepts through audio and phone-size visual
  acceptance. Extract and test a fast, low-cost match-ad recipe after that.
- North Star check (2026-10-27): holds; U4 attribution is unmeasured.

From `now-notes/2026-10-29-credits-1-16-0.md`:

# 2026-10-29: Control Center protocol 1.16.0, prepaid credits

Status: the protocol copy in `docs/control-center/` is Control Center's current one (1.16.0): the directive may carry a `credits` block and a report may carry `credits_spent[]` at `schema_version` 1.16.0. `docs/CONTROL-CENTER-BRIEF.md` names Full Time's shares (Higgsfield about 600 of 3,000 a month, Runway about 450 of 2,250, 21st Dev about 50 of 500), what to do and the walls. The engine is held, so the share applies only once Krish releases it. No engine code changed: reports still go out at 1.0.0 with no `credits_spent`.

Next: once Krish releases the engine, do Step 6 of `docs/GET-GOING.md`: read `credits`, spend the share on stills first, and report `credits_spent` at 1.16.0, proved against the stand-in.

North Star check (2026-10-29): holds.

From `now-notes/2026-10-29-credits-spending.md`:

# 2026-10-29: the credits step is built

Status: the runner reads the directive's `credits` into its activity (absent means unknown and nothing is spent), its guard refuses any spend past `remaining_for_you` or while held, and a report carries `credits_spent` at 1.16.0 only when a run spent, proved against the stand-in. The share itself is spent by one daily scheduled session (`docs/CREDITS-SESSION.md`) through Control Center's `reserve_credit_spend` and `settle_credit_spend`. The engine is held, so that session spends nothing until Krish releases it.

Next: when Krish releases the engine, enable its credits session and check the first settled spend lowers `remaining_for_you`.

North Star check (2026-10-29): holds.

From `now-notes/2026-10-29-held.md`:

# 2026-10-29: held until Krish releases it

Status: the engine honours a held activation state. When Control Center's directive or the tracked `activation.json` (held by default) says held, every `growth.py cc` report carries no proposals and exactly one `NOT_READY` hold naming the readiness gates: the rail at 4 of 6 AI Pundits, the release decision, D7, attribution, the workspace, and D1, which stays pending until its full-time decision-log entry exists. No ruling status changed.

Next: Krish records D1 in full-time's decision log, then an interactive session here sets its status in `rulings.json`; the hold lifts only when he releases it.

North Star check (2026-10-29): holds. The number is unmeasured (U4) and this change moves none of it; it stops five daily asks reaching his list while the engine is not ready.

From `now-notes/2026-10-30-channel-tasks.md`:

Status: The seven channel tasks are planned as GET-GOING Step 7, dormant behind the hold and ruling D1. No code, job or automation changed.
Next: when Krish releases the hold and clears D1, map the morning and weekly jobs onto the tasks.
North Star check (2026-10-30): holds.

From `now-notes/2026-11-10-codex-signin.md`:

Status: Claude sessions here show Krish a ChatGPT sign-in link and code whenever Codex is signed out (.claude/hooks/codex-login.sh at session start, cloud included); his subscription, never an API key (Krish, 2026-11-10).
Next: none for this; the first cloud session that uses Codex shows him the link and code.
North Star check (2026-11-10): holds.

From `now-notes/2026-11-11-instruction-and-state.md`:

Status: Control Center protocol 1.20.0 is built here. When the directive says features.engine_state, each report goes out at 1.20.0 with the engine's priorities (the North Star number this week against its target, then its open gates), Krish's quoted aims as obsessions, its next steps (the first open GET-GOING step, then NOW.md's "What is next") and acks of his instruction by id. The morning job pulls his instruction first (growth.py cc instruction) and records what it did (growth.py cc ack); his words stay in ignored local/. A dispatch's run id is unique per GitHub wake. The engine stays held, so an instruction is acked received, then blocked "Engine held".
Changed: engine/engine_state.py (new), engine/control_center.py, engine/reporting.py, engine/cli.py, jobs/morning.md, the morning automation's prompt, AGENTS.md, README, the brief, GET-GOING (Step 0 found done, Step 8 added), and the protocol copies in docs/control-center/ (1.20.0).
Next: on the first run after this merges (a dispatch or the morning job), read the stored report back and confirm it is schema_version 1.20.0 with priorities, obsessions and next_steps, and that Growth > Engines shows them.
North Star check (2026-11-11): holds.
