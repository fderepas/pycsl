# OPEN ROUTE #488 — mirror ghost handlers prove `assigns \nothing` through narrow trusted `_e` declarations

**Status: REPAIRED in the mirror (executor z1, driver run #3, 2026-10-30) — see §Repair record at the end. Was: OPEN, Severity 2 (a false proved FRAME clause in the self-annotation mirror; no consuming proof known).**
Found by executor dx1 (driver run #3, 2026-10-30) at Gate S of `getting-better/cross-mixin-declaration-stubs-impl.md`
(§5 Gate S record); see also the wall report `cross-mixin-declaration-stubs.md` and its review.

In `src/self-annotate/src/module6_whyml/expr_ghost_collections.py` (21 handlers) and `expr_ghost_spec_ops.py` (9), verified
handlers claim `#@ assigns \nothing` and call the `\trusted` cross-mixin DECLARATIONS `_e` / `_expr_to_whyml_string_ctx`,
which declare `assigns \nothing` while their definitions write ~22 fields. Widening the declarations to their definitions'
frames (R1) makes `expr_ghost_collections.py` fail Why3 typing (`depends on variable _pyobj_state, which is left out in the
specification`) and `expr_ghost_spec_ops.py` refused (writing self-call inside an opaquely-lowered comprehension): the
handlers' empty frames hold ONLY because the trusted declarations understate.

RUNTIME WITNESS (`witnesses-r488/frame_witness.py` + `w1..w8.py`, harness `runall.sh`): wrapping the LIVE handlers and
fingerprinting `vars(self)` around each call, `_handle_has_key_expr` writes `self._abstract_ops` (ensures using
`\has_key(\result, abs(a[0]))`, also `max(a)` / `sum(a)`) and `_uses_const_reflect_cache` (`int(s)`), while the mirror's
VERIFIED copy proves `assigns \nothing`. Controls: corpus 0295 0312 0785 0786 exercise the handlers with no write.
(The witness programs themselves fail L3-tc with `unbound ... 'abs_conv'` -- a separate fail-closed defect.)

Consumers: the handlers are dispatched by name; no proof is known to consume these 30 frames, so this is a false proved
clause, not yet a false proof of a relied-on fact.

REPAIR (measured in scratch): R1 on rows 1-3 TOGETHER with honest caller frames: the collections file then proves
166 Valid / 0 non-Valid (199 s). `_handle_mktuple_expr` (spec_ops) stays refused after widening -> re-trust it (+1
marker, honest) or model a writing call inside a comprehension. Then the declaration-conformance plane (R2a) keeps it fixed.

## Repair record (executor z1, 2026-10-30)

* The 3 local `\trusted` declarations (`GhostCollectionOpsMixin._e`, `GhostSpecOpsMixin._e`,
  `GhostSpecOpsMixin._expr_to_whyml_string_ctx`) WIDENED from `assigns \nothing` to their definitions'
  22-field frame (expressions.py `_e` / `_expr_to_whyml_string_ctx`). Nothing narrowed.
* The 30 callers carry that frame: 21 in `expr_ghost_collections.py`, 8 verified in
  `expr_ghost_spec_ops.py` + `_handle_mktuple_expr`, which stays REFUSED after widening (writing
  `self._e` inside an opaquely-lowered list comprehension) and is RE-TRUSTED with the honest contract
  (`assigns` = `_e`'s 22 fields; stub body). +1 `\trusted` marker (436 -> 437);
  `trusted-reasons.tsv` row `cost-scale:writing-call-in-comprehension`, cite driver-backlog
  "ROUTE #488 REPAIR".
* Whole-file proofs (HEAVY_LOW=1): `expr_ghost_collections.py` 166 Valid / 0 non-Valid (215 s);
  `expr_ghost_spec_ops.py` 122 Valid / 0 non-Valid (98 s).
* FOLLOW-UP (same day): the honest frames on 33 functions of these two opaque-int `@mutable_state`
  classes raised `check-assigns-writes-survival` TRAP 1443 -> 2169 (+726 = 33 x 22 dropped fields). Paid
  by DECLARING the 22 fields on both mixins (`@dataclass`; annotations copied from the
  Expression/StatementEmissionMixin declarations; the 8 declared nowhere else — `_late_content_ops`,
  `_last_hval_get_raw/_str`, `_uses_*_cache` x5 — typed from their live initialisers, emitted erased as
  `int` / `array int`; no handler reads them). TRAP -> 1399. Re-proved: collections 254 Valid / 0,
  spec_ops 144 Valid / 0 (whole-file, HEAVY_LOW=1). `expressions.mlw` byte-identical.
* Witnesses / controls: `witnesses-r488/repair_witness.sh <tree> <scratch>` (run via heavy.sh):
  C1/C2 repaired files type-check (PASS); W1 (`_handle_has_key_expr` re-narrowed to `\nothing`) and W2
  (`_handle_fst_expr` re-narrowed) FAIL Why3 typing (`depends on variable _pyobj_state, which is left
  out in the specification`); W3 (`_handle_mktuple_expr` un-trusted with its live body) is REFUSED
  (ir-semantic, writing call inside an opaque comprehension). All 5 AS-EXPECTED.
* Residual: the R2a declaration-conformance plane (keep local declarations' frames equal to their
  definitions') is NOT built here; `_handle_mktuple_expr` reopens on a modelled lowering of a writing
  call inside a comprehension.
