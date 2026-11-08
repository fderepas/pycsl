# STAGED — ROUTE #57's WITNESSES, HELD OUT OF THE CORPUS UNTIL THE REPAIR CAN LAND

Same reason as `getting-better/staged-route56/`: a corpus witness for an OPEN route is an
XPASS, and the harness has counted an XPASS as a failure since relaunch #44. The repair is
a `src/pycsl/module6_whyml/expressions.py` change and reference-suite run 6 is live.

## THE REPAIR, AS SPIKED AND MEASURED IN AN ISOLATED WORKTREE

A new helper `_dv_absent_opaque(nu)` beside `_dv_missing_default`, used at the TWO
one-argument `.get` sites (`expressions.py`, the self-field-dict twin and the
local/param dict):

  * `string` codomain -> route #50's existing `pycsl_none_str`
  * `int` (and untyped) codomain -> route #44's existing `pycsl_none`
  * every other codomain (`hval`, `seq …`, `map …`, `array …`, `emit_ir`) keeps the
    existing placeholder, DELIBERATELY: they were not measured, and route #56's lesson is
    that a carrier must be measured rather than assumed.

No new model, no new axiom, ledger stays 3. The TWO-argument form never reaches the helper
and stays exact, because there Python really does answer the supplied default.

## MEASURED SO FAR (isolated worktree, HEAD + the spike)

    1112  d.get(5) == 0          int codomain    SUCCESS -> FAILED   route closed
    1113  d.get(5) + 1           int codomain    SUCCESS -> FAILED   route closed
    1114  d.get(5) == ""         str codomain    SUCCESS -> FAILED   route closed
    1114b d.get("zz") == 0       str KEYS        SUCCESS -> FAILED   route closed
    1115  d.get(5, 7) == 7       positive control    SUCCESS -> **SUCCESS** (unchanged)
    ----  d[5] == 0              subscript path      SUCCESS -> **SUCCESS** (unchanged),
                                                     which is CORRECT and deliberate: the
                                                     missing-key SUBSCRIPT is the
                                                     language's documented opt-in
                                                     exception stance (`#@ no_exception
                                                     KeyError`), not this route, and the
                                                     repair must not silently annex it.

**ALL SIX MEASUREMENTS ARE IN AND THE REPAIR IS EXACTLY SURGICAL**: every one-argument
`.get` shape closes, at BOTH measured codomains and with both int and string keys; the
explicit-default form keeps proving; the subscript path is untouched.

## THE COST IS NOW MEASURED — SEVEN MIRRORS, AND IT IS REAL

`bin/mirror-emit-sweep.sh` + `byte-diff-compare.py`, baseline = a clean worktree at the
post-route-#56 HEAD, 53 of 53 emitted on both sides:

    ROUTE #57 ALONE:  7 MOVED — auto_trust, expressions, functions, preamble,
                      statements, stmt_control_flow, types — 0 GONE, 0 APPEARED.

That is exactly the 8 measured for #56+#57 together minus the 1 that was #56's, so the
separation arithmetic checks out against an independent measurement rather than being
assumed. **0 APPEARED matters most**: no file that was refused has become an emission,
which is the one direction that can only ever be a soundness loss.

SEVEN mirror re-proofs are therefore owed, and two of them (`expressions`, `statements`)
are the slowest in the tree — each has taken ~3-4h and neither had EVER completed before
this window. Budget a multi-hour battery, and do NOT land this while anything else needs
those two files' verdicts.

## THE ORIGINAL NOTE ON COST

`.get` is used heavily by the emitter's own source, so unlike route #56 this is very
unlikely to be byte-inert on the mirror. Run `bin/byte-diff-sweep.sh` twice plus
`bin/byte-diff-compare.py` (which since `681acc25` fails on MOVED / GONE / **APPEARED**),
and budget for mirror re-proofs. If the mirror moves, the honest cost is the re-proof, not
a narrowing of the repair to dodge it.

## LANDING SEQUENCE

1. Collect `suite49_run6.rc` and record its verdict.
2. Confirm 1115 (the positive control) is SUCCESS under the spike.
3. Land route #56's repair and route #57's together — both are in `expressions.py` and both
   reuse the same two existing opaques.
4. `git mv` both staged directories' witnesses into `test-suite/corpus/pycsl-reference/`.
5. L3 byte-diff; then `bin/run-soundness-planes.sh`; then update the 30th plane's baseline
   entry for `_dv_missing_default` from **OPEN** to CLOSED.
