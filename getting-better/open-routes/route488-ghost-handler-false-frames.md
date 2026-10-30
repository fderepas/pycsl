# OPEN ROUTE #488 — mirror ghost handlers prove `assigns \nothing` through narrow trusted `_e` declarations

**Status: OPEN, Severity 2 (a false proved FRAME clause in the self-annotation mirror; no consuming proof known).**
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
