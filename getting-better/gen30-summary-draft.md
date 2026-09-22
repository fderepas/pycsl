# gen #30 — summary DRAFT (to be finalised at the deadline, §A.3)

**Branch** `ghost-assign-bc6`. Nothing pushed; pushing stays gated to the user.

## Routes resolved (SEV-1, each with the decisive signature: a false contract PROVING while the TRUE twin is REFUSED, and CPython run as ground truth)

| # | what the model claimed | where |
|---|---|---|
| 191 | a `None` stored anywhere read back as the integer 0 | `expressions._expr_to_whyml`, the typed `NoneExpr` leaf |
| 192 | a genuine integer 0 was re-tagged as `None` at an `Optional`/union parameter | the two lifts that recognised `None` BY THE SPELLING `"0"` |
| 193 | the placeholder array for an unrepresentable iterable had a KNOWN LENGTH | `_array_coerce_arg`, the `"0"` arm |
| 194 | an erased collection was the integer 0, and an int-erased param's contract read it | `_coerce_to_int`, the array/map arms |
| 195 | the empty-list placeholder was the integer 0 at an int-erased param | `_coerce_dotted_args` |
| 196 | the empty-list placeholder was 1024 elements long at an `array int` param | `_coerce_dotted_args` |
| 197 | `getattr(o, "a", 0)` on an UNKNOWN-typed object answered the DEFAULT and the body read it | `expressions`, the getattr fall-through |
| 198 | a BARE `return` was the integer 0 | `stmt_control_flow._handle_return_stmt` |
| 199 | the EMPTY f-string `f""` was the integer 0 | `expressions._handle_fstring_expr` |
| 200 | a string literal actual was HASHED into a declared `int` param, and the hash ships in this repo | `_coerce_dotted_args` -> `_coerce_to_int` |
| 201 | a string actual became a ONE-ELEMENT array at a `List[int]` param | `_array_coerce_arg`, the TAIL |
| 202 | the same hash through an UN-ANNOTATED param, and through the KEYWORD slot | the #200 refusal's own two blind spots |
| 203 | a SINGLE-part f-string `f"{n}"` was the integer it interpolates | `expressions._handle_fstring_expr`, the int-model joiner |

## Planes added or collected

* `bin/check-argument-coercion.py` — every argument substitution classified PASS-THROUGH vs SUBSTITUTION, with a justification each.
* `bin/check-proof-reverify.sh` — the axiom-footprint gate. Its ratchet was driven **6 -> 0** (VERIFIED 155 -> 166: eleven `#@ proof` axiom imports nothing had ever checked).
* `bin/check-trusted-reasons.py` — a full plane that existed and **nothing ran it**; collected into the runner.
* `bin/check-return-boundary-substitutions.py` — the RETURN side, the gap `check-argument-coercion.py` names in its own header and `check-constant-fallthrough.py` names in its own. Pins occurrence COUNTS, and was demonstrated to fire on the pre-#198 tree via `--live`.
* `bin/check-corpus-contract-truth.py` — the value-differential's method (curate nothing,
  re-run CPython every pass) applied to BOTH REFERENCE CORPORA instead of to 75 curated
  drivers. **379** PASS-expected files across `pycsl-reference` and `python-reference`
  already carry a zero-arg function with a literal `#@ ensures \result == N`: **367 AGREE
  with CPython, 0 DISAGREE**, 12 unrunnable (a category — programs CPython
  cannot run, because they name `#@ datatype` types). That is FIVE TIMES the curated
  population, at no cost in drivers written. A failure here is the sharpest verdict the
  battery can give: a test that passes the prover while its own postcondition is false of
  its own program. There are none.
* `bin/check-coercion-exits.py` — the trigger rule's THIRD firing: `_array_coerce_arg` (#193, #201) and `_coerce_to_int` (#194, #200/#202) each produced two routes, and `check-argument-coercion.py` classifies the call SITES without ever looking inside the helpers. Pins both exit sets with counts; demonstrated to fire on the true pre-#201 source.
* `bin/check-fstring-lowering.py` — built because the campaign's own trigger rule fired: TWO routes (#199, #203) in ONE function in ONE session. Pins the return set with counts AND two structural tokens, because #203 added a *wrap* rather than an exit and the return-set half is green on the pre-#203 tree — a blind spot the `--live` self-test found before it shipped.

Battery: **18 -> 28 fast planes, 49 with `--slow`**, and `MIN_PLANES` tightened from a floor that carried slack to the exact count.
`check-swallowed-exceptions` ratchet **4 -> 0**, a hard zero.
Five new `value-differential` drivers (v73-v77), the CPython-measured plane, covering
#198, #199 and #203 in both the DISAGREE and the AGREE direction.

## Battery evidence

* Suite at `bc0561ec` (#198/#199/#200 + the return-boundary plane): **3823 / 3841**, 746
  XFAIL, **0 XPASS**, and the SAME 18 CONFIRMED FAIL this campaign has carried.
* Corpus byte-diff: ZERO pre-existing programs moved for every one of #198-#203.
* Mirror emission byte-diff: ZERO for #199/#200/#202/#203; exactly ONE file for #198 and
  ONE for #201, each the edited method's own mirror, each a one-line diff that is exactly
  the intended correction (M1).
* Fast planes: green after each of #198, #199, #200, #201, #202 and #203 (22/22, then
  23/23, then 24/24 as the last two planes were added).
* **Both moved mirrors RE-PROVED**: `module6_whyml/stmt_control_flow` (#198) —
  `Verification SUCCESS`, 12589 prover results; `module6_whyml/expressions` (#201) —
  `Verification SUCCESS`, **21347** prover results. M1 satisfied in both: the diff was
  exactly the intended correction AND the affected program re-proves.
* **gen11 differential fuzzer**: 60/60 seeds, **960 programs across the RETURN boundary**,
  ZERO false proofs — the honest negative for the boundary that produced #198.
* **gen12** (the STRING/INT representation boundary, where #199/#200/#202/#203 all live):
  40/40 seeds, **800 programs, ZERO false proofs**. With gen11 that is **1760 differential
  programs across the two boundaries this generation repaired**, finding nothing after the
  repairs.
* **gen13** (the STORE-AND-READ-BACK boundary, route #191's archetype generalised to
  fourteen store/read pairs): 560 programs, running.

## The method, in one sentence

Read a plane's — or a function's — OWN WRITTEN JUSTIFICATION as a checkable claim, and probe
it by giving the callee a contract that is TRUE OF ITS OWN BODY and that READS the property
the substitution changes. A callee with `ensures True` hides the entire family, which is why
the call boundary survived 190 routes.

## Lessons banked this generation

(a)-(g) from the first half; (h) difficulty is not soundness; (i) name which SPELLINGS were
run; (j) predict the TRUE twin, and give completeness its own witness; (k) the choke-point
rule is enforced by two ratchets; (l) build the plane the other planes named; (m) a repair
that fixes one arm leaves the rest of the function; (n) a residue you write down is a work
item; (o) the lesson you just banked applies to the fix you just shipped; (p) the upper bound is not the blast radius — read the arm, then count that shape; (q) a gate built from a route must be run against the pre-route tree.

## A surface opened this generation: the `pycsl_lib` stdlib layer

93 body-verified stub packages, governed by `config/skills/agent-stdlib-annotate`, with
**no gate in the 24-plane battery comparing a stub against the module it stands in for.**
Two instruments were built and run for the first time:

* `scratchpad/g30/stdlib_diff.py` — BODY differential. Its headline (129 "mismatches") is
  misleading and that is the finding: the stubs are ABSTRACTIONS, not re-implementations,
  so body equality is the wrong criterion. The control proves the harness works: `bsect`,
  the one package that IS a faithful re-implementation, matched `bisect` on 8000 inputs.
* `scratchpad/g30/stdlib_contract_diff.py` — CONTRACT differential, the right criterion:
  generate inputs satisfying `#@ requires`, run the REAL module, evaluate `#@ ensures`
  against CPython's answer. 2000 checks, **21 violations in 2 functions** —
  `mth.remainder` (claims `\result >= 0`; `math.remainder(8,5)` is `-2.0`) and
  `stat.filemode` (claims the constant `"----------"`; the real one returns `'?-------w-'`).

**Severity checked, not assumed, and downgraded:** `import_classifier._stub_set` reads only
the `.py` stems directly under `src/pycsl_lib/`, and no name map takes `math` to `mth`, so
nothing substitutes these contracts for a real stdlib import. They are documentation and
naming defects in standalone modules. The number that survives: **124 of 870 `pycsl_lib`
functions (14.3%) have a single-constant-return body** — harmless while nothing consumes
them as stdlib models, and exactly what becomes a hole on the day something does.

**AND THEN IT WAS BUILT**: `bin/check-stdlib-contract-fidelity.py`, the 26th fast plane.
The map is derived from the stubs' OWN headers (50 of the 93 name an importable stdlib
module) and restricted to 24 PURE, DETERMINISTIC modules — the exclusion is a SAFETY
property, since the gate calls the real function with generated arguments and `shutil`,
`subprocess`, `tempfile`, `os`, `io`, `signal` and `pathlib` are all in the header-derived
set. **5202 contract evaluations, 6 baselined divergences** — the two real defects above
plus four `csys` functions whose own header declares the 0..1000 integer scaling. It is
deterministic (fixed pools, no randomness — a sampling gate cannot carry a ratchet), guarded
at 4500 evaluations, and self-tested: `--selftest-empty-baseline` must exit 1, and does.

A SECOND stdlib plane followed, because the first one could not reach the sharpest set:
`bin/check-stdlib-pinned-facades.py` (the 27th). The differential gate CALLS the real
function, so `os` is on its safety deny-list — and `os` holds ten of the twelve functions
whose body is a single constant AND whose contract PINS that constant. That gate is pure
AST: **870 functions scanned, 12 facades baselined by name**, `os.islink -> 0` the sharpest
(a proof that nothing is ever a symlink). One entry is faithful and baselined anyway
(`sysmod.get_float_info_max_10_exp -> 308` is the right answer) because **the gate keys on
shape, not on truth**, and the baseline says so rather than leaving the next reader to
re-derive it.

Two documentation defects were also FIXED this session, both emission-byte-identical:
`mth.remainder` lost the false sentence "For integers, same as x % y" (IEEE rounds to
nearest, `%` floors), and `stat.filemode` was relabelled a ten-character placeholder with
the faithful fix PRICED (ten independent bit tests over a string model with no
per-character theory).

A THIRD stdlib plane followed from a question the first two provoked: does the campaign's
own headline metric reach this layer? **It does not.**
`bin/count-trusted-directives.py` globs `MIRROR/**/*.py` and `bin/check-trusted-reasons.py`
scopes to `src/self-annotate/src`, so the **459 marker count excludes `src/pycsl_lib/`
entirely** — and that layer carries two markers, one of them a BARE `#@ \trusted` with no
reviewer and no reason (`hlib.Sha256.update`, in a class whose `hexdigest` returns
`[0] * 64`). The skill for that layer says it carries ZERO trusted markers and that an
opaque kernel becomes an abstract `val` pinned by a cited `#@ proof`, never `\trusted`.
**The rule existed, the violation existed, and no plane connected them.**
`bin/check-stdlib-trusted-markers.py` (the 28th) now does, with the bare marker baselined
and its defect named rather than failed on arrival.

>>> A METRIC THAT DOES NOT REACH A DIRECTORY IS NOT A METRIC FOR THAT DIRECTORY.

What remains for the `agent-stdlib-annotate` owner is the judgement the gates deliberately
do not make: whether to give those twelve facades real bodies or weaker contracts, and
whether `hlib.Sha256.update`'s trust becomes a reviewer clause or an abstract `val`.

## Standing, deliberately deferred (re-priced this generation, not inherited)

* `check-avatar-frame-parity` (B) INHERITED segment: **7 sites, not 11**, none pre-stubbed —
  7 new markers plus a 5-6 iteration caller fixpoint over five mirrors, one at 8250s/proof.
* the hval absent-key sentinel's MIRROR side, left honestly OPEN with the next step named.

## CONVERSIONS: ZERO, AND THAT IS THE HONEST HEADLINE

The base self-tcb-reduction loop's metric is `\trusted` stubs CONVERTED to verified
methods, and this generation converted **none**: the count stands at **459**, exactly where
it started. What the window did instead was close **thirteen SEV-1 unsoundnesses** and add
**six planes**, and those are not a substitute for conversions — they are the other half of
the same job. A converted stub reduces what the verifier ASSUMES; a closed route fixes what
the verifier CLAIMS. A tree with 459 markers and no false proofs is in a better place than
one with 400 markers and six live routes, and the campaign's own rule — never re-baseline a
gate to make it green — is the same instinct applied to the metric: **do not convert a stub
while the emitter under it is still proving things that are false.**

Stated plainly so the next window can disagree with it: if the route yield drops, the
conversion track is where the budget should go, and the two deferred segments
(`check-avatar-frame-parity` (B), the hval absent-key mirror side) are priced and waiting.

## Metrics at the end of this session (measured, not recalled)

| metric | value | note |
|---|---|---|
| `\trusted` markers | **459** | unchanged across all six routes landed after the third kill — every repair was placed so it cost no marker |
| unmirrored live defs | **549** / 1823 (30.1%) | the mirror-coverage ratchet, unmoved (the two ratchets that caught #200's first placement) |
| `\trusted` stubs whose live body raises | 76, of which **62 SILENT** | a named ratchet, unmoved; reducing it moves callers' VCs and is a segment, not an increment |
| broad swallowing handlers that FIRE | **0** | driven 4 -> 0 this session; the baseline is now an empty set, a hard zero |
| axiom-footprint UNRESOLVED | **0** | driven 6 -> 0 earlier in the generation (VERIFIED 155 -> 166) |
| fast planes | **23** | MIN_PLANES tightened to the exact count |
| planes with `--slow` | **44** | |
| corpus | **1632** `.py` files | +14 this session, seven carrier/control pairs |
| value-differential drivers | **75** | +5 this session (v73-v77) |
| unpushed commits | see `git log origin/ghost-assign-bc6..HEAD` | **nothing pushed; pushing stays gated to the user** |

**The metric that did not move is the point.** Thirteen SEV-1 routes were closed this
generation without adding a single `\trusted` marker and without moving the coverage or
raises-honesty ratchets: every repair was either an opaque inside an already-effectful
method, a faithful value, or a refusal placed at a choke point whose mirror is already
trusted. Two planes (`check-mirror-coverage`, `check-trusted-raises-honesty`) enforce that,
and they caught the one placement that would have broken it.
