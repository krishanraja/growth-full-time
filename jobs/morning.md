# Morning batch

Kind `daily`, 06:15 London. The v2 loop (docs/ENGINE-V2.md): the engine reads, checks
and prepares; Krish answers in Control Center and posts by hand in Buffer (ruling 3).
Run `python3 growth.py sync` first when working interactively; `python3 growth.py run morning
--require-existing-history` includes it for a scheduled run. Read
AGENTS.md, the newest HANDOVER-*.md and docs/ENGINE.md first; `python3 growth.py
session pack --kind orchestrator --check` is the whole reading list, 36 KB or less.

1. Verify the existing persistent project and private ledger are available. Never
   start a fresh ledger (`--require-existing-history`).
2. Pull Krish's instruction before anything else: `python3 growth.py cc instruction`.
   It prints the instruction's id and a digest only, and keeps his words in the
   ignored `local/control-center/instruction.json`. When it says `act: true`,
   read that file and do what it asks first in this run, inside the walls: it
   never approves a send, post, spend, deletion or account change (AGENTS.md,
   "Krish's instruction" and rules 1 to 11), so anything at a wall becomes a
   proposal or a hold in the report. Record what you did with
   `python3 growth.py cc ack --state started --line "..."`, then `--state done`
   or `--state blocked`, each line in your own words: what you did, or why it is
   blocked and what would unblock it. Never copy his words into a tracked file,
   a commit, a pull request, a log, a report or an ack line. When it says held,
   do nothing on it: the report acks it received and blocked. (While Control
   Center holds the engine, the directive carries no instruction at all.) To
   update what Krish sees while you work, ack the same step again with a new
   line. Without a bearer it exits with `missing_token`; go on with the job.
3. `python3 growth.py run morning --require-existing-history`. Import an approved
   aggregate export with `--observations` only when its product, consent,
   provenance and window are verified. Missing collectors stay missing. Never
   inspect personal accounts.
4. `python3 growth.py actions`. It lists Krish's actions today (his answers first,
   then the posts he approved and has not made, then at most three one-off setup
   steps) and the engine's own to-do. While the engine is held, do none of the
   setup steps that would put an ask on his list. Do the engine's to-do in this
   run, in order:
   - **fixtures:** `python3 growth.py fixtures fetch`, or save Control Center's
     football-data reply and `python3 growth.py fixtures import FILE`. Never rank
     or time a take from memory (crew/match_clock).
   - **receipts:** read Buffer's posts on the Full Time allowlist only (read-only,
     `growth.py buffer query` then the Buffer connector's list_posts), then
     `python3 growth.py buffer receipts --posts FILE --pack FILE --channels FILE --record`.
     That closes each approved G2 whose kept items are all posted.
   - **north-star-line:** a scheduled run keeps the git tree clean, so it reports
     this one; the next interactive session records this week's measured number,
     or U4 if unmeasured, in a closeout note under `now-notes/` (NOW.md is never
     edited on a branch). Only Krish changes the North Star itself.
5. On HOLD, keep the changed constraint and at most three next actions; do not
   regenerate the same bank of held marketing. On a matchday with a newly
   published edition and a format in play in the signed spec, and only when the
   engine is not held, prepare that day's pack: the crew cards in play,
   `growth.py pack check`, then
   `growth.py pack propose --spec local/specs/<week>.signed.json --queue`.
   Draft per COPY.md (take test, passes A to E, rubric with the diagnosis in
   `why`) and apply [the listening standard](../docs/LISTENING-STANDARD.md) to
   source audio and the exact destination edition. Missing full-length listening
   evidence stays a creative-review hold; an audition is not a public-release
   approval. Build nothing mid-run: a missing part is a hold with its code, not
   new code.
6. Check and save drafts locally. Record actual publication URLs only after a
   human action. Keep Krish's day within twenty minutes; the actions list says
   when it is over, and then ask fewer things, never more.
7. End with `python3 growth.py cc morning --require-existing-history`. It
   journals a started attempt, pulls Control Center's directive, repeats the
   morning batch (a repeat keeps the same identities), reports (with the
   instruction's acks and the engine's state, protocol 1.20.0, and his actions
   and the North Star and Google Analytics readings as activity lines) with a
   digest readback, reads Krish's decisions and journals the end. While held it
   carries no proposals and one NOT_READY hold. Otherwise a creative saved in
   step 6 that passed every gate is proposed behind the post wall with its exact
   words; a held one goes in as a hold with its code. Nothing is sent, posted or
   spent. Queued G1 and G2 gates stay local until they are folded into this
   report (EXECUTION-PLAN.md, follow-ups). Without a bearer it exits with
   `missing_token`: say that reporting was unavailable; step 3 already saved the
   run locally.
8. Return a short checkpoint: the gate, Krish's actions today in plain words,
   what the engine did from its to-do, any changed dependency and the report's
   attempt status.
