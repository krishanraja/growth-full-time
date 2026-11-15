# Full Time growth execution and handoff

> **Status: background, written before engine v2 (27 October 2026).** Where this file disagrees with the Engine v2 rulings in [AGENTS.md](AGENTS.md) or with [docs/ENGINE.md](docs/ENGINE.md), those win. Its targets and channel limits are history; the live ones are in `docs/NORTH_STAR.md` and AGENTS.md.

The growth-side implementation of 17 October is complete, and the Control
Center loop, its later protocol steps and engine v2 are built on top of it;
what is still open is in docs/GET-GOING.md and in "Follow-ups from the v2
merge" below. Product implementation and Control Centre implementation belong
to separate sessions using the briefs below. Krish has held the engine since
29 October (AGENTS.md, "Held").
The engine never turns incomplete access or product gates into a success claim.

## Accepted boundaries

No personal social accounts, personal WhatsApp groups, cold outbound email,
prizes, new SaaS or paid media generation. Paid ads are not banned (Ruling,
Krish, 2026-11-15): one paid test waits on D5, which needs D7. Use verified Full
Time brand identities, voluntary listener sharing and inbound or explicit opt-in
product email. Target zero incremental marketing cash outside a paid test Krish
approves. Existing agent/hosting
costs remain real; unknown usage is reported as unknown.

All code changes stay in growth-fulltime. Full-time and Control Centre receive
briefs. No production release, product ruling or publication is approved by
this implementation. The old eight-job inventory and excluded channel banks
are retired from execution.

## Delivered engine components

| Component | Delivered implementation | Verification |
|---|---|---|
| Policy | Channel exclusions including held drafts; brand, consent, rail and separate release gates | Existing copy checks plus policy/failure-path tests |
| Measurement | Versioned aggregate input, exact windows, source freshness, mature cohorts and numeric rates with denominators | Missing/stale/zero, no sum of uniques, invalid cohorts and inconsistent rates tested |
| Creative history | Stable IDs, versions, actual human publication receipts and current-version publication status | Reruns and changed copy preserve historical proof without claiming new copy is published |
| Experiments | Immutable definitions, seven-day minimum, sample rules, negative results and inconclusive outcomes | Underpowered results cannot scale |
| Recovery | Atomic locked writes, revision checksums, backups and validated restoration | Concurrent writers, damaged primary and tampered backup tests |
| Reports | Control Center protocol reports from `growth.py cc` (attempts, directive, report with digest readback, decisions); the version 2 envelope and export stay as private local backups | Worked-example digest, strict schema, stand-in attempts, replay, readback, 409 and 401 tests; the bearer never appears in output |
| Rendering | Published-audio fetch, local deterministic match-card template, one/two editions, captions, thumbnail and source receipt | Actual FFmpeg tests and a real published-edition private preview |
| Orchestration | One morning batch and one Monday review; at most three actions, deterministic commands first | Complete live held runs and repeated-run checks |

See README for runnable commands, MEASUREMENT.md for query definitions and the
newest HANDOVER file for exact completion evidence and schedule status.

## What the next sessions implement

| Priority | Owner | Handoff and exit evidence |
|---|---|---|
| P0 | full-time | briefs/GROWTH-FOUNDATIONS.md: read stored verdicts for the newest drop; fix the smallest supported refusal; verify a fresh match with at least four published AI Pundits |
| P1 | Control Center | docs/CONTROL-CENTER-BRIEF.md: product isolation of packs for media review only; run reports already go through the protocol |
| P1 | full-time and existing collectors | MEASUREMENT.md: controlled visit, actual play, completion, comparison, reachable consent and mature return queries; source-scoped aggregates only |
| P1 | full-time | Exact-edition sharing/metadata, readable share-image fonts, recipient behaviour and optional permitted way back |
| P1 | Product owner | Verify an eligible opt-in/inbound tester pool, product inbox coverage and an actual brand identity; record product decisions in their source of truth |

The live rail is in state/FULLTIME-NOW.md, read hourly. On 12 November it had
four matches with one AI Pundit each, the newest from 19 October. Promotion
stays HOLD until a destination meets the four-of-six rail gate and
all other product, release, identity and consent gates pass. A ready pipeline
preflight is not the complete December release bar.

## Operating loop

The morning batch runs at 06:15 Europe/London; the weekly review Monday 08:00.
Each verifies the persistent private project, syncs once and uses approved
aggregate exports. A missing collector stays missing. No identical daily bank
of held promotion and no broad model-driven recurring research.

The first field milestone is thirty distinct consenting testers who finish a
show, followed through a complete seven-day window. The product's release bar
retains its actual thresholds. The 1,000 reachable-completer ambition for
8 November is not a forecast. Do not sum daily uniques, assume private forwards
or infer publication from a copied draft.

After release, begin with one branded YouTube format: two real arguments from
the same match, published audio, AI disclosure, one reachable mobile path and
actual publication evidence. Read completed listens and mature return alongside
attention, costs and human minutes before adding formats or channels.

Each task ends with `growth.py cc`, and Control Center's daily wake-up runs
the same loop on a clean runner; it does not wake the engine while Krish holds
it. Delivery means an accepted report whose
read-back digest matches. The private bundle from `growth.py export` is a
local backup, not the hand-off and not proof of delivery.

## Follow-ups from the v2 merge (15 November 2026)

Ruling (Krish, 2026-11-15): Full Time v2 lands on main keeping main's Control
Center report. These parts of v2's report logic were not folded in, because
each would change main's report design rather than add to it. Each is one pull
request against `engine/reporting.py` and `engine/control_center.py`, proved
against the stand-in in `tests/test_control_center.py`, and none is needed
while the engine is held (a held report carries no proposals).

1. **G1 and G2 in the report.** `engine/gates.py` queues the weekly spec (G1),
   the matchday pack (G2) and a Codex card's allowance spend, and the loop
   settles his answers to them, but `reporting.build` does not carry
   `gates.pending()`, so they never reach his list. Fold them in as proposals
   once the report can carry a `stage`.
2. **Stages and `parent_proposal_id`.** v2 raised the report to 1.1.0 for
   `stage` (plan, go_live, check_in) and checked each stage's wall
   (`protocol_errors`). Main's report goes as 1.0.0, 1.16.0 or 1.20.0 and
   carries no stage. Add stages inside main's version choice, never as a
   second version rule.
3. **One ask at a time on the engine's side.** v2 kept what waits on Krish's
   list in the ledger (`still_waiting`, `waiting`), deferred a second ask of a
   kind already waiting (`one_ask`) and never re-asked an answered digest
   (`answered`, `answered_before`, `answered_in`). Control Center already shows
   one ask per engine (`oneTurnEach`); decide whether the engine needs its own.
4. **The standing ruling order D7, then D2, then D3**, and retiring the
   release ask once D1 or ORGANIC is approved (`standing_order`,
   `release_retired`). Main's report still asks the release decision while
   `policy.release_open` is false. Since 15 November D5, the paid test, is
   among the pending ruling asks, so with three actions and the release ask
   the report keeps two of its ten proposal slots for the weekly kill list
   (`reporting.build` cuts at ten).
5. **Declined posts hold no slot.** v2 skipped an action Krish had already
   answered on its digest, so three declines never blocked a fourth post.
6. **The capabilities check** (`GET capabilities`, refusing a report version
   Control Center does not offer, and reading `autonomy`).
7. **The read window's fifteen-minute overlap** (`read_from`): main reads his
   decisions from the last read time exactly.
