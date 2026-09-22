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
* `bin/check-fstring-lowering.py` — built because the campaign's own trigger rule fired: TWO routes (#199, #203) in ONE function in ONE session. Pins the return set with counts AND two structural tokens, because #203 added a *wrap* rather than an exit and the return-set half is green on the pre-#203 tree — a blind spot the `--live` self-test found before it shipped.

Battery: **18 -> 23 fast planes, 44 with `--slow`.**
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
* Fast planes: 22/22 green after each of #198, #199, #200, #201, #202 and #203.

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

## Standing, deliberately deferred (re-priced this generation, not inherited)

* `check-avatar-frame-parity` (B) INHERITED segment: **7 sites, not 11**, none pre-stubbed —
  7 new markers plus a 5-6 iteration caller fixpoint over five mirrors, one at 8250s/proof.
* the hval absent-key sentinel's MIRROR side, left honestly OPEN with the next step named.
