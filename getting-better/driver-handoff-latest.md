# Driver handoff — gen #31, 2026-09-25T23:50Z

Deadline **2026-09-27T08:19Z** (epoch 1790497192, written, never recomputed). Do not push.
~32 h left at the time of writing.

`$S` = `/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad/g31`

## READ THIS FIRST — the session's own conversion track failed an audit

`bin/run-soundness-planes.sh` has a FAST set (48) and a SLOW set (25, `--slow`). **Every gate
script this session ran the fast set only** — twenty-eight invocations, gates A through N, each
printing "all 48 plane(s) green". Run once with `--slow` at 21:48Z on the increment-N tree:
**5 of 73 RED**, and two of the five were conversions those same gates had banked.

SIX conversions landed this session were hollow and are now RE-TRUSTED (`d21a61fb`):

    pure_ast.py::_Parser.error                erased=['msg'] of ['msg']
    pure_ast.py::_Parser.unsupported          erased=['what'] of ['what']
    Module2_Parser.py::_ContractParser._err   erased=['msg'] of ['msg']
    monomorphize.py::_rewrite_call_sites      erased=BOTH args
    module6_whyml/identifiers.py::stable_hash erased=['s'] of ['s']
    pure_ast.py::iter_fields                  `let ... : unit`, the yielded pair dropped

Two of them had the verdict written in the file already and the converting commits left the
comment saying "STAYS trusted". See
`getting-better/open-routes/finding-eleven-gates-over-four-red-oracles.md` and wall-lesson (q6).

**RULE FROM HERE ON: a gate runs `--slow`, or it is not a verdict on a conversion.**
`bin/run-soundness-planes.sh` now says so in its own summary line (`5857acff`).

## What is running right now

| job | started | log | expect |
|---|---|---|---|
| increment-O gate (`$S/gate_o.sh`, **runs `--slow`**) | 23:44:05Z | `$S/gate_o.log` | byte-diff vs `bd_n`; mirror vs `mir_n` with FIVE declared movers; fidelity **895**; planes 73/73; suite **4029/4047**, the standing EIGHTEEN, ZERO XPASS |

## Committed since the last handoff (in order)

    60a32f79  449 -> 446 — three `pure_ast.py` dunders and a constructor
    3139c714  the whole conversion frontier, measured — 230 type errors, four walls
    85bfa846  increment N GATED — 4029/4047
    bf75103b  the FIELD value model already landed — the wall is its CLOSURE
    ff7aed38  FOUND — eleven gates over four red oracles
    d21a61fb  REVERT — six hollow conversions re-trusted, 446 -> 452
    900ff447  452 -> 451 — the string closure + `errors.py::__str__` (FOUR symbols)
    5857acff  the fast battery names its own scope
    4ff23661  progress log
    f4b495f0  route #213's two witnesses registered (a RED that predates this session)

## Standing numbers after increment O (pending the gate)

    markers                    451
    verbatim un-trusted        895
    trusted-or-dependent       828   (ratchet 828, raised 798 -> 830 naming six members,
                                      then tightened to 828 by the one conversion)
    silent-termination          56   (ratchet 56)
    untrusted-emitted          922 un-trusted, 0 `val`, 0 absent, 0 inside a trusted parent
    reasons TSV                451 rows, unclassified 442 (ratchet 442)
    emitted-vacuity            0 new erasures (9 known, gated)
    yield-erasure              0 value-erasing, 2 suspension (ratchet 2)
    shadowed-selfcalls         14 (ratchet 14), 119 bypassing sites

## The one RED still standing, and it is NOT this session's

`check-stdlib-modules-verify.py` — 104 modules, 83 verify (FAILS 6, REFUSED 13, TIMEOUT 2).
The battery truncates its stderr, so WHICH of its two failure modes fired
(`NEWLY NOT VERIFYING <module>` vs `NO-ENSURES COUNT GREW`) is NOT YET KNOWN. It is a ~25-minute
prover plane; run it alone after gate O:

    . scratchpad/g29/env.sh && python3 bin/check-stdlib-modules-verify.py 2>&1 | tail -30

**It has NOT been ruled out that the string-closure patch (`900ff447`) caused it** — the 21:48Z
battery ran with that patch already in the working tree. Gate O's own `--slow` run answers this;
if it is still RED there, bisect against `85bfa846` before doing anything else.

## Next, in order

1. Confirm gate O. If the corpus byte-diff MOVED, the string closure is not inert and must be
   re-examined before anything else — its inertness argument is that a corpus
   `if self.<strfield>:` already emits the ill-typed `<> 0` and so cannot be in a passing
   program, which is an argument, and the sweep is the measurement.
2. Resolve `check-stdlib-modules-verify` (above).
3. Re-screen the 103 markers whose recorded verdict was a `string`/`int` type error, to measure
   what the string CLOSURE actually retires: `$S/rescreen_facade.txt` (76, facade ports) and
   `$S/rescreen_differs.txt` (27, `--replace` ports). Run `$S/screen_port.sh <list>` then
   `$S/recheck_ports.sh` — NEVER trust the screen's own blacklist filter (wall-lesson: it
   scored "cannot be applied" as a pass).
4. **Every candidate that survives the screen must ALSO pass `--slow` before it is banked.**
   The four oracles that matter are `check-emitted-vacuity`, `check-yield-erasure`,
   `check-shadowed-selfcalls` and `check-untrusted-emitted`. Check 1 (the emit-diff, four
   clauses) does NOT subsume them: it admitted all six of the hollow conversions above.
5. Backlog #59 names the four capabilities that would retire those six honestly — the exception
   PAYLOAD model, the generator SEQUENCE model, the receiver-erased `.get` on a dict-typed
   parameter, and `#@ sibling_concrete` for a `NoReturn` helper.

## Discipline reminders that cost this session time

* one short step per Bash call; `timeout 43200` on every detached prover run
* never `git add -A`; never glob a directory you did not create
* kill by PID, never `pkill -f` / `pgrep -f` with a pattern that matches your own shell (c6, m6)
* check free space before `cp -a src` and delete the previous copy (a full /tmp produced a FALSE
  SOUNDNESS ALARM)
* the tracked modified `.aux`/`.olean` files under `test-suite/corpus/**/rocq|lean` are BUILD
  OUTPUT, deliberately left — do not revert or `rm` them
* `. scratchpad/g29/env.sh` sets `$S`; use a different variable name in your own scripts
