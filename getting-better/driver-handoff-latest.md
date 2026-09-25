# Driver handoff — gen #31, 2026-09-25T04:04Z

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


---

# UPDATE 04:04Z — increments D, E and F are all COMMITTED; only the gate is outstanding

    af7f32c1  D  two `\trusted` markers RETIRED and PROVED (460 -> 458)
    594aa07d  E  the frame plane's external-effect half (16 stubs that shell out)
    e8f33b10     the yield plane descends too (a trap closed while empty, 0 population)
    f184e94f  F  the integrity gate checked 863 of the 915 it was meant to; the walk now
                 descends, `FOLDED` is a shape, a STATIC refusal for a closure inside a
                 `\trusted` parent, and TWO HONEST MARKERS take the count back to 460
    3213c4f1     progress log

## The session's accounting, stated so it cannot be misread

    460  session start
    458  `errors.py::message` and `proof2why3/sertop.py::__exit__` PROVED (all four checks)
    460  `_hdr_name` and `_returns_literal_none::walk` take honest markers — they are
         un-trusted closures inside `\trusted` parents, verified by nothing
    886 -> 888 -> 886 verbatim un-trusted

Two functions left the trusted set by being proved. Two joined it by being found never to have
been verified. **The count is unchanged and the map is two entries more accurate.**

## The gate, when increment A's suite finishes

    nohup bash $S/gate_d.sh > $S/gate_d.log 2>&1 &

Baselines `bd_nw` / `mir_nw` (the increment-A gate's own output). `--expect-moved errors
sertop` on the mirror compare — and that list is MEASURED, not guessed: `$S/emit_pair.sh`
emitted both newly-marked files from the working tree and from `f184e94f^` and both are
**INERT, byte-identical**. A closure folded into an opaque `val` emits the same with or
without its marker.

PREDICTIONS: corpus **0 MOVED**; mirror moves exactly `errors.mlw` and `sertop.mlw`; all 48
planes green; suite **4029/4047**, the standing EIGHTEEN, ZERO XPASS.

## Still open

* `ir_schema.py::validate_ir` — check 1 REFUSES (20 new abstract ops, `ir_keys_0 ()` nullary).
* `pycsl.py::_finalize` — check 1 returns a BYTE-IDENTICAL emission; converting it would prove
  nothing. Do not convert it.
* the 36 TYPE errors from the verbatim screen — being sized by kind right now
  (`$S/type_detail.log`); they are the container/field value model in one voice.
* the 11 DIFFERS at >= 0.80 similarity — a mechanical re-port, then the same screen.
* `check-mirror-signature-drift.py` still stops at a `def`; covered elsewhere by the fidelity
  plane, which compares signatures and descends.

---

# UPDATE 04:20Z — increment G is fully specified and pre-checked; it is the next thing to do

The D+E+F gate's plane battery went 2-of-48 red and both reds were right (a new `\trusted`
marker owes a row in `trusted-reasons.tsv` and a line in the termination ledger). Fixed in
`74f5db2c`; battery re-running; the D+E+F suite is running in `$S/gate_d.log`.

## Increment G — the I4 fixpoint (a set's element type)

**Why it is next.** All 62 verbatim `\trusted` candidates are screened and ZERO remain
landable behind a proof alone. The frontier is capabilities, and this one is already measured,
already carried by three files in `check-open-route-carriers.py`, and its landing instructions
were written by a previous window inside the carrier file itself:

> WHEN THIS FILE STARTS VERIFYING, the I4 fixpoint has landed. Move it and its controls into
> the corpus as witnesses in the SAME commit, lower `check-open-route-carriers.py`, and record
> the mirror re-proof bill.

**The patch** (`$S/land_i4b.py`, two parts, both hunks verified to apply exactly once):
1. `frontend/Module5_IREmitter.py` — the PARAMETER κ extractor calls `_m5_get_field_key_type`
   instead of `_m5_get_dict_key_type`, so a `Set[str]` PARAMETER gets κ from its DECLARATION.
   The FIELD extractor already covers `Set[str]` and says why — *a set's element IS its key*.
2. `module6_whyml/functions.py` ~137 — drop the `_mut_coll` conjunct. It existed because a
   read-only set param's κ could only come from the USAGE tagger, so promoting it desynced the
   sibling `val` bridges. With κ read from the declaration, both ends of a call edge get it
   from the same place. **That is the fixpoint — by construction, not by a propagation pass.**

**The order.** (1) D+E+F gate green. (2) `bash $S/land_i4.sh` — applies the patch and runs the
three carriers directly. The carrier must flip FAILED -> SUCCESS and BOTH controls must STAY
SUCCESS; **if a control moves, STOP** — the mechanism is not what the carrier says it is
(wall-lesson a6). (3) Move all three into the corpus as 1909/1910/1911 with
`# pycsl-expected: PASS`, delete their three entries from `check-open-route-carriers.py` and
lower its count. (4) Gate against `bd_d`/`mir_d` with `--expect-moved 0884` on the corpus and
the ten mirror movers named from `$S/mir_i4b.log`. (5) **THE BILL: re-prove all ten moved
mirror files**, each detached with `timeout 43200`.

**The measured bill.** Corpus 1 mover (`0884`, from a TARGETED 81-file comparison — declare it
and let the gate name any others). Mirror 10 movers:

    Module6_WhyMLTranspiler (~41m)   frontend____init__ (~24m)   frontend__ir_resolve (~22m)
    frontend__monomorphize           module6_whyml__expr_ghost_collections
    module6_whyml__expr_ghost_spec_ops   module6_whyml__expressions (~2h57m — the dominant term)
    module6_whyml__functions         module6_whyml__statements    module6_whyml__stmt_control_flow

Estimate 6-8 hours of prover time. Suite predicted **4032/4050** (4029 + three new witnesses).

**THE REFUSAL THAT GOVERNS IT.** If a moved mirror file stops proving, the increment does NOT
land by marking that file `\trusted`. That would be trading a real proof for a marker in order
to buy a capability — the exact inverse of this campaign. Record the regression and stop.

---

# UPDATE 04:37Z — increment H: the PORTING vein, and it does not need a capability

`proof2why3/sertop.py::__enter__` was taken end to end on an offline tree: a ONE-LINE port
(`return None` -> `return self`), an 11-line all-additive emit diff identical in shape to
`__exit__`'s, and `[+] Verification SUCCESS!`. Then all 50 facades with a live body of ten
lines or fewer were ported and screened: **12 PORT AND LOWER**, 32 TYPE errors, 5 refusals,
1 syntax. `getting-better/open-routes/finding-twelve-facades-that-port-and-lower.md`.

## Land these four FIRST — they call no trusted sibling

    frontend/Module2_Parser.py   _err          (check 1 done: 34 diff lines, ZERO new `val`,
                                                and it converts TWO functions — the ported body
                                                calls `_contractparser__cur`, which was sitting
                                                unemitted as a `val` and becomes a `let` too)
    frontend/Module2_Parser.py   _try
    frontend/pure_ast.py         error
    frontend/pure_ast.py         unsupported

The other eight would be relabelled trust-DEPENDENT rather than shrinking the surface, because
each calls a `\trusted` sibling — `parse_contract` calls `parse`, `_rewrite_call_sites` calls
`_rewrite_subscript_calls_in_stmt`, `interleave` calls `next`. That is exactly what
`errors.py::message` did, and it is why `MAX_TRUSTED_OR_DEPENDENT` exists. Land them, but land
them knowing the aggregate will not fall.

## The tools

    $S/port_one.py        replaces a mirror function's BODY with its live twin's, keeping the
                          mirror's own `def` line and `#@` lines. `--convert` also deletes the
                          marker by LINE PREFIX. ABORTS rather than guessing — and a CRASH now
                          prints `ABORT:` too, because the first version crashed before writing
                          and the screen reported ten false `**PORTS+LOWERS**`.
    $S/check14_port.sh    emit BEFORE -> port+convert -> emit AFTER -> diff -> NEW-`val` list
                          -> REAL whole-file proof. One offline tree, cleaned first.
    $S/screen_port.sh     the batch screen, sentinel-stoppable.
    $S/port_cheap.txt     the 50 (live body <= 10 lines)
    $S/port_rest.txt      the 185 (live body > 10) — screening now

## The order for increment H

1. `check14_port.sh` each of the four clean candidates; require ZERO new abstract ops and a
   green whole-file proof.
2. Land them on the live tree with `port_one.py . <rel> <fn> --convert`.
3. Checks 2 and 3: `count-trusted-directives` 460 -> 456, `check-self-annotate-sync` 886 -> 890,
   the three trust planes, **and `check-untrusted-emitted.py`** — a ported function must come
   back `LET`, not `val`, and that plane is now the one that can tell.
4. `trusted-reasons.tsv` loses four rows (they are `unclassified`, so MAX_UNCLASSIFIED falls
   456 -> 452 and should be lowered).
5. Gate with `--expect-moved frontend__Module2_Parser frontend__pure_ast` on the mirror.
   Corpus predicted 0 MOVED; suite unchanged.

---

# UPDATE 05:45Z — D, E and F are GATED; increment H has FIVE PROVED candidates

**D+E+F gate, 05:15Z:** corpus inert in all three directions, mirror moving exactly the two
declared files, fidelity 886, all 48 planes green, suite **4029/4047**, the standing EIGHTEEN,
ZERO XPASS, no flaky recoveries.

## Increment H — ready to land, adjudicated one at a time

PROVED on an offline tree (port the live body, delete the marker, emit diff with ZERO new
abstract ops, then a REAL whole-file proof):

    proof2why3/sertop.py::__enter__               1-line port
    frontend/Module2_Parser.py::_err              converts TWO functions
    module6_whyml/identifiers.py::stable_hash     1-line port, 27 diff lines
    proof2why3/parser.py::__repr__                1-line port, 13 diff lines
    frontend/monomorphize.py::_rewrite_call_sites

REFUSED, and each for a named reason:

    proof2why3/sertop.py::_sexp_tokens            Z3 TIMEOUT 30s, 7,433,789 steps
    proof2why3/from_sexp.py::_find_construct_idx  Z3 TIMEOUT 30s, 3,193,221,587 steps
    frontend/pure_ast.py  (5 together)            CHECK 1: three new abstract ops —
                                                  `get__fields`, `isinstance_op`,
                                                  `_const_types_not_get_2`; proof `Unknown
                                                  (why3: Out of …)`

STILL RUNNING: `pure_ast.py::error` + `unsupported` ALONE (check 1 already clean — 28 diff
lines, ZERO new ops, two `val`->`let`), and `module6_whyml/expressions.py::_emit_metatype_tags`
(that file's proof is ~3h).

## To land increment H

    bash $S/land_ports.sh proof2why3/sertop.py:__enter__ \
        frontend/Module2_Parser.py:_err module6_whyml/identifiers.py:stable_hash \
        proof2why3/parser.py:__repr__ frontend/monomorphize.py:_rewrite_call_sites

PREDICTIONS: count 460 -> **455**; fidelity 886 -> **891** (five ported bodies become verbatim);
`check-untrusted-emitted` must report each as LET, never `val`; `trusted-reasons.tsv` loses
five `unclassified` rows so MAX_UNCLASSIFIED falls 456 -> **451** and should be lowered.
Gate with `--expect-moved proof2why3__sertop frontend__Module2_Parser module6_whyml__identifiers
proof2why3__parser frontend__monomorphize`; corpus predicted 0 MOVED; suite unchanged.

## Then increment G

`$S/try_i4.sh` is dry-running the I4 patch on an OFFLINE tree right now — the carrier must
flip FAILED -> SUCCESS and both controls must stay SUCCESS.

---

# UPDATE 07:00Z — increment H is landed and gating; increment G is scripted and dry-tested

## H (commit `5559aedd`) — 460 -> 455, five markers retired by PORTING

Checks all green before the commit: count 460 -> **455**, fidelity 886 -> **891**, raises 61
silent (was 62), frame OK, termination 55, blast-radius **834 -> 817**, and
`check-untrusted-emitted` **0 `val`, 0 absent, 0 inside a trusted parent** over 918 functions.
`trusted-reasons.tsv` synced to 455 rows, MAX_UNCLASSIFIED 456 -> **451**.

Gate (`$S/gate_h.log`, started 06:14Z): corpus **0 MOVED** in all three directions, mirror
**5 MOVED, 0 unexpected** (the five emission names declared correctly first time), fidelity
891, **all 48 planes green**; suite started 06:29Z.

## G — scripted, dry-tested, waiting only on H's suite

    $S/land_i4_live.sh     applies the two-part patch, `git mv`s the three carriers into the
                           corpus as 1909/1910/1911, drops their rows from the carrier plane,
                           proves the three witnesses, and re-checks the count and fidelity
                           (which must NOT move — this is an EMITTER change, not a mirror one)
    $S/drop_setelem_rows.py  the carrier-plane edit. DRY-TESTED ON A COPY: the value closes on
                           the same line as its last string, and a first pattern expecting
                           `    ),` removed ZERO rows — the assertion caught it on the copy
                           rather than on the live plane. 12 carrier rows -> 9.
    $S/witness/            the three corpus witnesses, each control's docstring stating what
                           its FAILURE would mean

The dry run on an offline tree already showed the carrier flipping FAILED -> SUCCESS with both
controls holding.

**THE BILL, and it is the reason G is a multi-hour increment:** ten mirror files move and each
must still PROVE — `Module6_WhyMLTranspiler` (~41m), `frontend____init__` (~24m),
`frontend__ir_resolve` (~22m), `frontend__monomorphize`, `module6_whyml__expr_ghost_collections`,
`module6_whyml__expr_ghost_spec_ops`, `module6_whyml__expressions` (~2h57m),
`module6_whyml__functions`, `module6_whyml__statements`, `module6_whyml__stmt_control_flow`.
Corpus: 1 mover (`0884`, from a TARGETED 81-file comparison — declare it and let the gate name
any others). Suite predicted **4032/4050**.

**THE REFUSAL:** if a moved mirror file stops proving, G does NOT land by marking that file
`\trusted`. Record the regression and stop.

## Still running

    $S/cm_pureast2.log   `pure_ast.py::error` + `unsupported` — check 1 already clean (28 diff
                         lines, ZERO new ops); whole-file proof running 1h30+
    $S/cm_expr.log       `expressions.py::_emit_metatype_tags` — proof running 1h50+ (that
                         file's mirror proof is ~3h)
