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
    1115  d.get(5, 7) == 7       positive control    MEASUREMENT IN FLIGHT at the time
                                                     this file was written — the box is
                                                     saturated by suite run 6 and two
                                                     mirror proofs. **It must be SUCCESS.
                                                     Do not land the repair without it.**

## THE COST IS NOT MEASURED AND IS EXPECTED TO BE REAL

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
