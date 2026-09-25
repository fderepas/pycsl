# Driver handoff — gen #31, 2026-09-25T03:46Z

Deadline **2026-09-27T08:19Z** (epoch 1790497192, written, never recomputed). Do not push.

## What is running right now

| job | started | log | expect |
|---|---|---|---|
| increment-A gate, SUITE stage | 03:11:21Z | `$S/gate_new.log` | `SUITERC=` ~04:17Z; predicted **4029/4047**, standing EIGHTEEN, ZERO XPASS |
| the verbatim conversion screen | 03:37:36Z | `$S/screen_verbatim.log` | 58 candidates, ~54 done |
| increment-D checks (two stubs) | 03:43:51Z | `$S/land_two.log` | ends with `DONE`; count already 460 -> **458** |

`$S` = `/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad/g31`

## Committed since the last handoff

    594aa07d  the frame plane's EXTERNAL-EFFECT half — 16 stubs that shell out under
              `assigns \nothing`, all named; plus the 5 NESTED stubs the walk cannot reach
    e7e45f7f  the facade census — the conversion population is not 410
    3422e737  the second wave — 11 stale copies, 89 a different program
    b3c637a2  backlog #53
    9e343d15  CORRECTION — 56, not 61; the census keyed on bare names
    eaddcd79  backlog #53 carries the correction

## Increment D, UNCOMMITTED IN THE WORKING TREE

Two `\trusted` markers retired, both having PASSED CHECK 1 (the emit-diff):

    errors.py::message              val -> let; 4 assumed frame `ensures` become PROVED; the
                                    only new `val` is `str_dunder_op ()`, exactly the opacity
                                    the old `val` already had.
    proof2why3/sertop.py::__exit__  val -> let with body `()`; 4 assumed frame `ensures`
                                    become PROVED; NO new `val` at all; the LIVE body really
                                    is `pass`. 11 diff lines, every one additive.

NOT `audit_proof_reverify.py::_cache_root` — it lowers AND proves, and check 1 refuses it:
its `os.mkdir` becomes `val root_mkdir_0 () : int`, nullary, with no `writes`.

Also uncommitted: `bin/check-trust-blast-radius.py` gains **MAX_TRUSTED_OR_DEPENDENT = 833**.
Retiring `message` did NOT shrink the trusted surface — `message` is
`return super().__str__()` and `errors.py::__str__` is itself `\trusted`, so the function
moved from "trusted" straight into "trust-dependent" and the old ceiling broke 400 -> 401 on
a conversion that helped. Both ends moved (dep_lo 335 -> 336), so it is not an artifact of
the by-name over-approximation. The aggregate `trusted + dep_hi` is invariant at 833 across
the change and is now the ratchet that means what the campaign means. Verified non-vacuous:
set to 832 the plane prints NOT OK.

## The sequence from here

1. Wait for `SUITERC=` in `$S/gate_new.log`. Predicted 4029/4047. Record it in
   `getting-better/driver-progress.log`.
2. Wait for `DONE` in `$S/land_two.log`. Required: frame-honesty OK, blast-radius OK at the
   new aggregate, fidelity **886 -> 888**, and BOTH files print `Verification SUCCESS`.
3. Commit increment D (the two conversions + the blast-radius ratchet) as ONE increment.
4. `nohup bash $S/gate_d.sh > $S/gate_d.log 2>&1 &` — baselines `bd_nw`/`mir_nw`, and
   `--expect-moved errors sertop` on the mirror compare. Corpus predicted **0 MOVED**;
   suite unchanged at 4029/4047.
5. Then work the remaining verbatim LOWERS hits through check 1:
   `ir_schema.py::validate_ir` and `pycsl.py::_finalize` (the latter is one of the 5 NESTED
   stubs). `$S/check1.sh <rel> <fn>` does the emit-diff and cleans its own tree first.

## Standing refusals

* `pkill -f` — kill by PID; the screen stops with `touch $S/STOP_SCREEN`.
* before any `cp -a src`: check free space, delete the previous tree. `check1.sh` refuses
  below 400M. The failure mode a full /tmp produced was a FALSE SOUNDNESS ALARM.
* never `git add -A`; never glob a directory this session did not create.
* the modified tracked `.aux` files under `test-suite/corpus/pycsl-reference/*.proofs/rocq/`
  are BUILD OUTPUT, left deliberately. Do not revert or remove them.
* `--no-proof` LOWERS is a NECESSARY CONDITION AND NOTHING MORE. In one hour it was wrong
  three ways: over a facade, over a generator, and over `_cache_root`.
