# Full Time now

Read from `krishanraja/full-time` at commit `708cc284e4` and from fulltime.fm on 2026-11-18T22:04:01+00:00 UTC by `python3 growth.py sync`.
Rewritten when a sync finds full-time, its open pull requests, the rail or the feed changed. The full-time repository and the live site are the source of truth; this is a reading of them.

## Push gate: HOLD

No match has 4 of 6 AI Pundits (newest: 1 of 6). A push sends fans to a match only when at least 4 of the six AI Pundits made a show for it (PLAYBOOK.md, "The rail gate").

## The rail at fulltime.fm

| Match | Shows on | AI Pundits | Made a show |
|---|---|---|---|
| Tottenham 3-1 Coventry | 2026-10-19 | 1 of 6 | The Reporter |
| Crystal Palace 3-1 Nottingham Forest | 2026-10-11 | 1 of 6 | The Reporter |
| Manchester City 5-3 Sunderland | 2026-09-20 | 1 of 6 | The Romantic |
| Tottenham 2-3 Aston Villa | 2026-09-19 | 1 of 6 | The Gaffer |

## Krish's actions

His matchday and plan answers wait in Control Center; `growth.py actions` lists them with the rest. From what this public reading can see:

- Rule on D7 in Control Center: Close the PostHog and Google Analytics consent item.
- Switch Full Time to handcrafted in Control Center (one click), so every approved post comes back to you to post by hand. (1 min, one-off)
- Listen to the whole Liverpool v8 mix once, on headphones, and give it one verdict: post it, change it (say what), or bin it. It is session/outputs/Liverpool-v8-mid-broadcast-TV-mix.mp3 in the session archive in Drive Growth Build/06_Reference/creative-handoff/2026-10-27/ (HANDOVER-2026-10-27-CREATIVES.md). (3 min, one-off)
- Approve briefs/2026-10-27-decision-log-rulings.md and start a full-time session with it, so the per-take ruling (D1 and ORGANIC) comes into force. (2 min, one-off)
- Approve the two product briefs (share attribution and rail supply) so a full-time session can build them. (5 min, one-off)
- Create the Full Time handles on YouTube (a Brand Account), TikTok and Instagram (Business) first, with one handle everywhere and the brand inbox, never a personal email. Then reserve Threads, X, Facebook and a WhatsApp Channel. (30 min, one-off)
- Connect the three Full Time channels to Buffer and put their Buffer channel IDs in local/buffer-channels.json (copy examples/buffer-channels.example.json). (10 min, one-off)
- Start a Control Center session with briefs/2026-10-27-control-center-measurement.md, so its directive carries ga4_landings and registers the two new objective keys. (2 min, one-off)
- Run the Cowork prompt in briefs/2026-10-27-cowork-canva-brand-kit.md on your PC: the Full Time brand kit and six templates in Canva, built from the approved social kit. (20 min, one-off)
- Let a session on your PC run scripts/baseline.py over your Codex and Claude logs, so the 20x cost target has a real baseline. (5 min, one-off)

## Rulings the playbook needs

| Ruling | Here | In full-time's decision log | In force |
|---|---|---|---|
| D1: Invite-led at scale: testers and every shared edition invite others; fan channels open | approved | no | no |
| D2: Cover every Premier League match each weekend, not one a day | pending | no | no |
| D3: Sign-up after the first finished show, and the morning recap for beta users | pending | no | no |
| D4: Name Full Time under Krish's own name: LinkedIn, Show HN, Product Hunt, press | pending | no | no |
| D5: Paid creators (up to £600) and one paid test (up to £300) | pending | no | no |
| D6: FPL "Beat the AI Pundits" league, framed as a game, never as forecast performance | pending | no | no |
| D7: Close the PostHog and Google Analytics consent item | pending | no | no |
| ORGANIC: Organic brand posts recruit pilot-beta testers before the December release, gated per take | approved | no | no |
| RELEASE: The product release decision | pending | no | no |

## Latest decisions (full-time `docs/12-roadmap.md`)

- 2026-10-26 - Solo analysis first; paid conversation after quality and adoption
- 2026-10-16 - A pilot beta for fans, a December target, one feedback inbox
- 2026-09-27 - Premier League only, one match, no scroll
- 2026-09-05 - Publish the pundits that passed
- 2026-09-04 - Launch by founder override
- 2026-08-10 - One documentation hierarchy

## The Reporter feed

- Thu, 22 Oct 2026: Take the points. Keep the bigger claims on hold.
- Mon, 12 Oct 2026: A comfortable result, an uncomfortable process

## The canon, in order

1. `docs/22-vision-and-beta.md`
2. `docs/12-roadmap.md`
3. `docs/00-product.md`
4. `docs/21-go-to-market-agent.md`
5. `docs/07-marketing.md`
6. `docs/01-brand.md`
7. `docs/product-state.json`
8. `NOW.md`
9. `docs/19-release-state.md`
10. `docs/09-growth.md`
11. `docs/11-legal.md`
12. `AGENTS.md`

## Recent commits on main

- none since the last sync

## Work in flight (open pull requests)

- #115 Sync the canon block (`harness/canon-sync`, updated 2026-11-18)
