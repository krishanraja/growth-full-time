---
repo: krishanraja/growth-fulltime
product: Full Time growth engine
as_of: 2026-11-24
head: a3fe056
lifecycle: building
production_url: none
state_doc: README.md
history_log: docs/history/LOG.md
truth_files: [docs/NORTH_STAR.md]
authority_order: [docs/NORTH_STAR.md, README.md]
steward: https://github.com/krishanraja/ai-harness/blob/main/docs/steward/RUNBOOK.md
---

# Full Time growth engine: where it is right now

## What it is

Full Time's growth engine: it drafts the moves that bring football fans to Full Time, and nothing it makes sends or posts on its own.

## Who it is for and why it matters for Mindmake

Football fans who become Full Time's returning listeners. It proves Mindmake can grow a product with drafted, approved moves at close to no cost.

## Where it is right now (as of 2026-11-24)

<!-- north-star-state {"week_of": "2026-11-09", "week_target": 30, "current": null, "current_as_of": "2026-11-12", "current_source": "Not measured: Full Time share links are not yet joined to new listens", "urgency": 4, "urgency_reason": "current number unmeasured"} --> **North Star number: U4, unmeasured.** New listeners this week who arrived through a fan's shared link or clip: unknown, against 30 this week, on the way to 1,250 by 25 January 2027. Nothing measures it yet: Full Time's share links are not joined to new listens (MEASUREMENT.md, and Step 3 of docs/GET-GOING.md). To measure it, full-time must export one weekly aggregate, metric `attributed_new_completers` (MEASUREMENT.md, "The North Star number", lists its exact fields): new identities whose first completed show came through a shared link, joined on the link's `utm_*` tags.

Lifecycle: building, and held. Krish held the engine on 29 October 2026 (Ruling, Krish, 2026-10-29: Not ready means a held activation state): Control Center's registry says held and so does the tracked `activation.json`. Control Center has not woken it since. On 14 November a hand-started run of the loop proved the held path live: Control Center accepted it as `held`, at 1.20.0, with no proposals and one NOT_READY hold, carrying the engine's priorities, obsessions and next steps. No workspace run has ever reached Control Center: its 13 reports are 12 dispatches from 19 to 29 October and that run. So Control Center shows this file's "Where it is right now" and "What is next" as the engine's state of play.

- The North Star has one name, `attributed_new_completers`, in code, specs, objectives, NOW.md, MEASUREMENT.md and the revenue and insight desks. It is the key reporting.py sends and Control Center registers; the v2 name `share_arrived_new_listeners` in engine/attribution.py was never registered and is retired (the dated briefs keep it with a note). GA4 rows are refused for an explicit set of listener metrics, the North Star included, instead of by a `_listeners` suffix. (2026-11-24)
- humour-engine and divergent-thinker are wired through Control Center on this engine's own bearer, dormant until capabilities serve features.humour and features.divergent. The morning batch scores its prepared captions against the published ones and records what went out (engine/divergent.py, namespace growth-fulltime:copy), both with no model call; paid moves (map, provoke, challenge, diverge) run only at will with `python3 growth.py divergent`, refuse while held, and a Control Center cap answer is final. `python3 growth.py humour check` reads a caption (at_person, needs_explaining, forced) and never rewrites it; unavailable is never a pass. config/insight-desk.json names both routes. (2026-11-24)
- The revenue desk adapter is in (Ruling, Krish, 2026-11-24): config/revenue-desk.json sets this engine's stage to measure first, since no step is counted and Full Time has no paid step, and its one output is the reading plan for attributed_new_completers: the weekly aggregate full-time owes, how growth.py imports it and where engine/measurements.py and engine/reporting.py score it. Bands are unset assumptions that bind only after Krish's yes, and spend_authority is none. tests/test_revenue_desk.py and the self-test check the adapter parses and its sources exist. (2026-11-24)
- Closeout notes fold again after every merge: the fold moved from check.yml into closeout-fold.yml, which runs on a push to main, after each Auto-merge run and by hand, so notes merged with the Actions token no longer pile up as they did from 14 to 24 Nov (2026-11-24). (2026-11-24)
- The insight desk is wired into Full Time (Ruling, Krish, 2026-11-24). `config/insight-desk.json` is the adapter (humour unavailable, divergent through the connector only in growth-fulltime:ideas, the first sheet a measurement idea while U4 is unmeasured); `engine/insight_sheet.py` checks a sheet; `python3 growth.py spec propose --insight <sheet>` names the sheet's lead on the G1 plan without changing the spec or its digest. Without the flag nothing changes, proved byte for byte against the previous commit's output (tests/golden/). With INSIGHT_DESK_SKILL set, methods are checked against the skill's list. The skill is still a candidate in ai-harness, so get_skill does not serve it yet. (2026-11-24)
- Engine v2, approved on 27 October, is on main (Ruling, Krish, 2026-11-15: Full Time v2 lands on main keeping main's Control Center report). The signed spec, the matchday pack, Google Analytics through Control Center, the Audience Builder, the social kit lock, the crew of eleven and the 27 October rulings now sit beside main's report design: held mode, the NOT_READY hold, engine state at 1.20.0, credits, AI answers and the wake suffix. Folded into that report: the North Star and Google Analytics readings, Krish's actions (only when not held) and the weekly library reconcile as activity lines, LIBRARY as a hold when not held, Google Analytics rows kept out of the completers objective, the ORGANIC exception and the three pushed platforms in the holds, the 1.x refusal, the amended_sha256 check, approved go-lives kept as his instructions, and his answers settled against the queued G1 and G2. The engine stays held; nothing was sent, posted or spent. (2026-11-15)
- paid ads are gated, not banned (Ruling, Krish, 2026-11-15): a paid draft waits on D5, D7, RELEASE and the rail, and D5 is an ask once the engine is released. From the Claude Ads review (docs/CLAUDE-ADS.md), `growth.py links audit` checks read-only that tracked links keep their tags when they land, and `growth.py learning plan|cost` says how long a test needs and what each counted event cost. Its first live run found every show link's share card is the site card. (2026-11-15) (2026-11-15)
- A weekly branch sweep (`.github/workflows/branch-sweep.yml`, Sunday 03:17 UTC, and by hand) deletes every remote branch whose work is already on main and lists each branch it keeps with why: unmerged work, an open pull request, protected (Ruling, Krish, 2026-11-15). The script is `.github/scripts/branch_sweep.py`, copied unchanged from ai-harness, which holds the canonical copy. (2026-11-15)

## What changed recently

- 2026-11-24 engine/attribution.py, engine/measurements.py, engine/spec.py, specs/campaign.schema.json, the synthetic example, MEASUREMENT.md, docs/ENGINE-V2.md, tests and the propose golden file.
- 2026-11-24 engine/divergent.py, engine/humour.py, engine/control_center.py (capabilities, divergent, humour, Control Center's refusal code), engine/insight_sheet.py, growth.py, config/insight-desk.json, requirements-humour*.txt, tests/test_divergent_humour.py.
- 2026-11-15 engine/control_center.py, engine/reporting.py, engine/engine_state.py, jobs/morning.md, automations.json, check.yml (Python 3.9 and Windows jobs beside the fold), tests/test_decisions.py (replaces tests/test_protocol_v11.py), the invariant registry and its register, AGENTS.md, README, CHANGES, EXECUTION-PLAN (seven follow-ups), GET-GOING, the brief and docs/ENGINE.md.
- 2026-11-15 Krish asked which Claude Ads capabilities genuinely help Full Time, and said "Full Time does not ban paid ads"; the code had refused the ads channel since 17 October.
- 2026-11-12 Krish, 2026-11-12: "make sure everything's a cohesive system and that the project documentation is 100% up to date with absolutely nothing old or misleading left in there".
- 2026-11-12 Krish asked whether the documentation was up to date, every word. It was not: NOW.md had stopped at 27 October with six notes waiting and no fold to write them in, the brief still said the engine was switched on with dispatch on, the third obsession was a summary of his words rather than his words, and the hourly sync's commits would have marked NOW.md unreconciled two days after every update. Each is fixed, and the sync now commits as chore(heartbeat).
- 2026-11-11 Protocol 1.20.0 (PR 19). Ruling (Krish, 2026-11-11): every growth engine's priorities, obsessions, next steps and outstanding items feed live across Control Centre, and he instructs each engine with his next best action. The morning job now pulls his instruction first (`growth.py cc instruction`) and records what it did (`growth.py cc ack`); his words stay in ignored `local/`, and a dispatch's run id is unique per wake.
- 2026-11-10 Claude sessions here show Krish a ChatGPT sign-in link and code whenever Codex is signed out (`.claude/hooks/codex-login.sh`, commit 05d8b8b), so Codex runs on his subscription, never an API key.
- 2026-10-30 The seven channel tasks joined the plan as Step 7 of docs/GET-GOING.md (PR 18), dormant while the engine is held and until D1 clears. Krish asked for each saved Instagram growth prompt to be its own task, defined once in ai-harness `contract/channel-tasks.md`.
- 2026-10-29 The credits step was built (PR 16). Krish chose "Scheduled sessions" to spend the share: the runner only reads it and refuses any spend past `remaining_for_you` or while held, and a report carries `credits_spent` at 1.16.0 only when a run spent.
- 2026-10-29 Protocol 1.16.0, prepaid credits (PR 15). Ruling (Krish, 2026-10-29): a growth engine may spend up to its share of credits already paid for, with no per-batch approval. Full Time's shares are about 600 Higgsfield, 450 Runway and 50 21st Dev credits a month (docs/CONTROL-CENTER-BRIEF.md).
- 2026-10-29 Held until Krish releases it (PR 14). Full Time is a few weeks from being in motion, so each report carries no proposals and one NOT_READY hold naming the readiness gates. It stopped five daily asks reaching his list for an engine that is not ready.

## What is next and what is waiting on Krish

- Next (2026-11-24): full-time exports one measured whole-week `attributed_new_completers` row, and MEASUREMENT.md's two join descriptions (utm tags at the top, the share token's 7-day first touch below) are settled to one with full-time.
- Waiting on Krish (2026-11-12): the release decision and D1, each recorded in full-time's decision log, and a full listen to Liverpool v8 (HANDOVER-2026-10-27-CREATIVES.md).
- North Star check (2026-11-24): holds.

## Read next

- `docs/NORTH_STAR.md`: the North Star, its number and its weekly ladder.
- `README.md`: what this repository is and how it runs.
- `docs/GET-GOING.md`: the build, step by step, and which steps wait while held.
- `docs/CONTROL-CENTER-BRIEF.md`: how this engine reports to Control Center.
- `docs/history/LOG.md`: what this file used to say, verbatim.

## Do not trust

Do not treat a successful render, technical media pass or historical review-ready
receipt as current creative approval. Do not read the prior listener count as a
fresh attribution measurement, or an empty local reporting export as delivery.
Do not read the 7 proposals in Control Center's 29 October report as live
asks: they predate the hold, and a held engine's asks never reach his list.
`briefs/CONTROL-CENTRE-HANDOFF.md` was superseded on 18 October by
`docs/CONTROL-CENTER-BRIEF.md`, and `briefs/2026-10-22-media-credits.md` on 29
October by the prepaid credits ruling and `docs/CREDITS-SESSION.md`. The
creative next action in `HANDOVER-2026-10-26.md` was superseded on 27 October by
`HANDOVER-2026-10-27-CREATIVES.md`.
