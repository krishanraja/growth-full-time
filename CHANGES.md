# Changes Krish made to the growth engine

Newest first. Record his words with the date, then change the job file and
`automations.json` together. A ruling (D1 to D7) is recorded here with his
words, and in `rulings.json` with the full-time decision-log heading that
records it.

- 2026-11-15: engine v2 lands on main, keeping main's Control Center report.
  Ruling (Krish, 2026-11-15): Full Time v2 lands on main keeping main's Control Center report. His words:
  "keep main's report". Everything v2 built on 27 October (the signed spec, the matchday pack, Google
  Analytics through Control Center, the Audience Builder, the social kit lock, the crew of eleven and the
  27 October rulings) is now on main beside main's report design: held mode, the NOT_READY hold, engine
  state at 1.20.0, credits, AI answers and the wake suffix. From v2's report logic, the parts that fit
  main's protocol were folded in: the North Star and Google Analytics readings, Krish's actions (only when
  not held) and the weekly library reconcile as activity lines, LIBRARY as a hold when not held, Google
  Analytics rows kept out of the completers objective, the ORGANIC per-take exception and the three pushed
  platforms in the holds, a refusal of any protocol major other than 1, his amended version checked by
  amended_sha256, an approved go-live recorded as his instruction, and his answers kept and settled
  against the queued G1 and G2. The 1.1.0 ask logic (stages, one ask at a time, the D7, D2, D3 order, G1
  and G2 in the report, the capabilities check) is not in the report; EXECUTION-PLAN.md lists it as
  follow-ups. The engine stays held, and nothing was sent, posted or spent.

- 2026-11-12: the docs match the engine, and closeout notes fold into NOW.md.
  Krish, 2026-11-12: "Is everything done? Are the project documentations up to date, 100%, every single
  word, with what this engine now is and how it works? Are there any other small bugs that you discovered
  that you just randomly left open?" NOW.md, README, AGENTS.md, the brief, GET-GOING, the credits session,
  the execution plan and the morning job now say what the code and Control Center do: the engine is held,
  Control Center has not woken it since 29 October, and no workspace run has reached it. The third
  obsession now quotes his own words of 17 October instead of summarising them. `growth.py closeout`
  checks and folds the closeout notes (engine/closeout.py, the fold job in check.yml); the six notes that
  had waited since 29 October are in docs/history/LOG.md. A repeated ack with a new line is now recorded,
  as Control Center accepts since protocol 1.21.0, the copy in docs/control-center/ is 1.21.0, and the
  hourly sync commits as `chore(heartbeat)` so the harness never marks NOW.md unreconciled for it. No
  job, schedule, ruling or wall changed, and the engine stays held.

- 2026-11-11: Control Center protocol 1.20.0, Krish's instruction and the engine's state.
  Krish, 2026-11-11: "Ensure the priorities, obsessions, and next steps for all the growth engines are
  feeding live to this dashboard, and not just in the growth tab. They are responsible for driving the
  overall success of each venture, so make sure I can instruct each one with my next best action and have
  it get going (as well as always understand the current state of play and what's outstanding). ... Get
  building". The morning job now pulls his instruction first (`growth.py cc instruction`) and records what
  it did (`growth.py cc ack`); the morning automation's prompt says so. Reports carry the acks and the
  engine's priorities, obsessions and next steps when the directive asks. His words stay in ignored
  `local/`. No wall moved and the engine stays held.

- 2026-10-30: the seven channel tasks join the plan as GET-GOING Step 7, dormant while the engine is
  held and until D1 is cleared. Krish asked for each of seven saved Instagram growth prompts to be its
  own task for every growth engine's specialists, defined once in ai-harness `contract/channel-tasks.md`.
  No job, automation or code changes.

- 2026-10-29: the credits step is built.
  Krish, 2026-10-29: "Scheduled sessions". `engine/credits.py` reads the
  share and guards any spend; the daily session in docs/CREDITS-SESSION.md
  spends it through Control Center's reserve and settle, never while held.
  No job, schedule or wall changed.
- 2026-10-29: Control Center protocol 1.16.0, prepaid credits.
  Ruling (Krish, 2026-10-29): a growth engine may spend up to its placement
  share of a tool's prepaid credits each cycle with no per-batch approval, and
  reports what it made. The protocol copy in `docs/control-center/` is now
  Control Center's current one, and docs/CONTROL-CENTER-BRIEF.md names Full
  Time's shares. While the engine is held it spends nothing. No code, schedule
  or wall changed.
- 2026-10-29: the engine is held until Krish releases it.
  Ruling (Krish, 2026-10-29): Not ready means a held activation state: no
  wake, no asks on his list, no growth council move, and the bearer stays
  valid. Full Time is a few weeks from being in motion. While Control Center's
  directive or the tracked `activation.json` (held by default) says held,
  each report has no proposals and one `NOT_READY` hold naming the readiness
  gates: the rail at 4 of 6, the release decision, D7, attribution, the
  workspace, and D1, still pending until its full-time decision-log entry
  exists. No ruling status, schedule or wall changed.

- 2026-10-27: the social kit's AI disclosure is enough as it stands. Krish, asked
  whether take clips also need "synthetic voices" as the old renderer said: "Ai
  pundit is fine". The kit shows "AI Pundit" on every frame and "Made by AI from
  checked match facts" on every plate. The kit's spec still has the audio say "an AI
  Pundit on Full Time" by 2 seconds, and the Voice Lock lint checks it within 5.
- 2026-10-27: approved the Full Time social kit, "The Switch, revision 1". Krish,
  shown the rendered kit cold: "I like it. Looks good." Each AI Pundit is a channel
  in its own paper; the default post is one channel and never claims a disagreement,
  and the cut and Pundit v Pundit render only when two real shows exist for the
  match. It lives in `brand/social-kit/`, pinned by `LOCK.json`; a change is a new
  revision he approves. The approval record, with every frame's SHA-256, is in
  Drive `Growth Build/05_Brand-Kit`. Posting, Canva uploads and spend each still
  need their own yes.
- 2026-10-27: Google Analytics comes from Control Center. Krish: "just get google
  analytics data from control center, much easier". Read live that day, Control
  Center has no Analytics read yet, so `briefs/2026-10-27-control-center-measurement.md`
  asks it to carry the week's landings in the engine's directive (`ga4_landings`); the
  engine reads that field now. The GitHub keyless route below stays as an unused
  fallback and is off Krish's list.
- 2026-10-27: Google Analytics moved off per-session access. Krish: "I need a
  more robust way of connecting Google Analytics than just in this session. That's
  so fragile. Can it not go in GitHub or Vercel?" The daily control center loop in
  GitHub Actions now signs in to Google keylessly (workload identity federation, no
  key or secret anywhere, accepted only from this repository's main branch) and
  reads aggregate landings read-only; Vercel was not used, because the engine's
  scheduled runs live in GitHub. Setup: `docs/GA4-ACCESS.md`, route A, and
  `scripts/ga4-github-setup.sh`. The per-session secrets step is gone.
- 2026-10-27: added the Audience Builder and a direct Google Analytics reader.
  Krish: "there needs to be a social media specialist working relentlessly: not
  necessarily to publish content, but to make sure that my profile is as visible
  as possible, with as many followers as possible, through all the different
  tactics". Profiles: "Full Time brand profiles (Recommended)". Growth work:
  "Automate within platform rules": official APIs only, each action type ruled by
  him first, in `engagement-actions.json`, with the risky types banned in code.
  Google Analytics: "Happy to let you read Google Analytics directly", then
  "Direct read-only API (Recommended)"; setup in `docs/GA4-ACCESS.md`.
- 2026-10-27: approved engine v2 and recorded nine rulings.
  Ruling (Krish, 2026-10-27): "approved, do it all" for [docs/ENGINE-V2.md](docs/ENGINE-V2.md).
  His decisions that day, in his words where given: going live "Go now, per-take
  gate (Recommended)" (D1 approved, new ORGANIC entry; in force once full-time's
  decision log carries the heading); accounts "Reserve all, push three
  (Recommended)"; publishing "i will do it in Buffer, but not until the voices,
  scripts and the video/image ad creatives are ready to be replicated easily and
  reliably"; roles "Claude handles planning, strategy, orchestration, whilst codex
  handles creative production and social media management"; the 11/10 bar built
  against the remote-switch ad, take clips, rows and match-morning cards;
  production on his machine; ready after "3 in a row, no edits"; brand match ads
  may link to Today; each format goes live on its own readiness; "knowing what
  works and what doesnt is CRITICAL"; a full Canva brand kit; every asset and
  strategy in the Drive Growth folder with no sprawl; Google Analytics as part of
  measurement. The Drive library `Ventures/Full Time/Growth Build` now has its
  fixed tree, START-HERE and INDEX, and the 27 October creative handoff moved,
  unrenamed and with its file IDs intact, into `06_Reference/creative-handoff/`.
  Nothing was posted, sent, scheduled or spent.

- 2026-10-26: connected creative releases to the product-owned personality core.
  Exact committed exports are verified and imported without activation; linked
  character variants receive only their selected core identity plus shared
  reusable speech. A changed product pin expands regression review. Core identity
  changes belong in the actual product; ad-only execution remains scoped here.
- 2026-10-26: added the offline creative continuity system.
  Ruling (Krish, 2026-10-26): "Build the engine, not the session."
  Separate versioned character and shared-style owners, pinned releases,
  scoped artifact judgments and regression gates now live behind
  `growth.py standards`. Actual dialogue, source media and review history stay
  under ignored `local/creative-system/`; the public schema and tests use no
  production creative. Technical success cannot override a human rejection.
  No schedule, channel, generation, product or Control Center authority changed.

- 2026-10-19: the copywriting, offers and demand corpus is now working knowledge.
  Krish: "all of these growth engines need to be imbued with this knowledge".
  Both files are preserved byte for byte in `knowledge/` and registered in
  `knowledge/sources.json`; repository verification and a unit test check
  their size and SHA-256. `COPY.md` applies the corpus to this engine and
  lists where its rules override it. PLAYBOOK.md, both job files and AGENTS.md
  now point drafting and review at it. No schedule, automation, contract,
  policy gate or Control Center behaviour changed.
- 2026-10-19: adopted the Control Center growth engine protocol.
  Ruling (Krish, 2026-10-19): "make each engine adopt its brief now".
  This supersedes the 17 October brief-only rule for run reports only: the
  engine now journals attempts, pulls its directive, reports with a digest
  readback and reads decisions through `growth.py cc`, at the end of both
  workspace tasks and on Control Center's daily `cc-growth-directive`
  dispatch (`.github/workflows/control-center.yml`). Packs stay local. The
  third morning action is now the release decision, since the reporting
  integration it named is done. Nothing sends, posts, spends or publishes,
  and an approval is recorded, never executed.
- 2026-10-17: completed the growth-side engine and made Control Centre a brief-only handoff.
  Ruling (Krish, 2026-10-17): "you are not to do any actual work in control-center, only pass me a brief once you have completed your work".
  Ruling (Krish, 2026-10-17): "Complete this all to 100% without coming back to me again."
  Enforced exclusions in code, removed remote report writes and the old eight-job
  setup, added durable history/recovery, aggregate measurement, experiment rules,
  local rendering, two consolidated jobs and a complete handoff contract. Product
  and release dependencies remain explicit; no product ruling was approved.
- 2026-10-17: verify existing access before requesting new credentials.
  Krish: "You should have full access to Vercel and all my projects.
  GROWTH_ENGINE_TOKEN is also in the github secrets". All eighteen Vercel
  projects are visible. The existing sync workflow now has a manual,
  read-only reporting check using that Actions secret. It skips sync writes
  and keeps credentials and report content out of logs. Authenticated reading
  does not waive the product-isolation requirement for report delivery.
- 2026-10-17: Control Centre is the unified reporting and action destination.
  Krish: "Control Centre is ultimately where the unified dashboard is going
  to be: where you report back on progress and recommendations to improve in
  the format that it requires." He also asks to be told when its UI cannot
  make recommendations actionable. E00 now proves access and native delivery;
  the private Control Center integration brief is pull request #470. Existing
  aggregate reads come before browser fallbacks, and local checkpoints do
  not count as dashboard delivery.
- 2026-10-17: execution plan and product build briefs, with the channel and
  cost limits carried into AGENTS, the playbook, browser rules and README.
  Krish: "Okay can you line up the execution plan? Just bear in mind that
  this cannot use my personal social media accounts and no cold outbound
  email. This needs to be as low cost and close to free as possible."
  The active plan targets £0 incremental marketing cash, uses Full Time's
  product and brand identity, and defers paid and founder-account channels.
  No product ruling or schedule is activated by the plan.
- 2026-10-16: a handover for the setup session (`HANDOVER-2026-10-16.md`),
  which `AGENTS.md` now tells every run to read after itself. Krish: "just
  save all of this in to the repo so the next codex session can go from here
  and set up the autonomous engine".
- 2026-10-16: the engine is built from the document in `knowledge/`. Krish
  attached "Full Time: The 1,000 Free Users in 30 Days Playbook" with the
  instruction below. Its seven decisions (section 9) are in `rulings.json`,
  all pending.
- 2026-10-16: a dedicated repository, the growth engine for Full Time. Krish:
  "now build out growth-fulltime repository as the dedicated growth engine
  for this app, obsessed with getting this into market". Built on the
  pattern of `growth-heartside`: drafts only, every run synced to the
  full-time repository first, a checker for Full Time's own rules, and
  scheduled Codex or Cowork runs.
