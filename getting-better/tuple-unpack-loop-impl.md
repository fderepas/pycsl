# Impl plan: for-loop TUPLE-UNPACK target-projection binder

Ref: `tuple-unpack-loop.md` (report) + `tuple-unpack-loop-response.md` (independent review, Gate R PASS).

## Spike — DISCHARGED (no further spike; cite review §3)
The make-or-break (does the faithful seq-of-pairs dual-binding loop prove?) is answered YES by the
review: hand `.mlw` `Valid` on Alt-Ergo (0.06s/0.15s) + Z3, in BOTH element models; and the EXACT
emitter-emitted `probe_c_pairs.mlw`, patched with ONLY the `.field0/.field1` bindings, proves
`Valid (0.04s, 17 steps)`. The emitter already lowers `List[Tuple[str,str]]` to
`type pytuple_str_str = { field0: string; field1: string }` and already emits the loop skeleton +
element read `let _for_target = ref (params[!_idx__for_target])`. Only the target projections are
missing. The loop proof carries no E-matching risk (17-892 steps). Spike GATE = PASS.

## Build (live emitter, gated)
1. In the dual-binding for-loop emit path (`_handle_for_stmt` / the tuple-target branch,
   `src/pycsl/module6_whyml/stmt_control_flow.py`): when the iterable element is a `pytuple_*` record
   (the loop skeleton already binds `_for_target = <iter>[idx]`) and the loop targets are a tuple,
   emit one projection binder per target — `let <t_k> = ref (!_for_target).field<k> in` — matching the
   existing enumerate/items dual-binding shape.
2. **Element string-type threading (review §4 co-gap):** register each string-typed tuple target in
   `_string_local_vars` (as `_enumerate_seq_recv` already does for the seq element) so body
   comparisons (`t != ""`) stay faithful strings, NOT int-hashed (`<> 313406155`). Without this the
   binder is emitted but the body is unfaithful → a facade → Gate C reject.
3. **Gate for byte-inertness:** gate the new binder branch on `_uses_/_emitting_<target-stub>` name
   sentinel (the `_uses_dictlit` shape) so no corpus program's emission changes. Note (review §7.2):
   `pytuple_str_str` emission is ALREADY live for corpus annotations, so only the NEW binder branch
   must be shown inert — the emitting-method gate is the control.

## Make-or-break for the BUILD = END-TO-END single-stub conversion (review §7)
The binder-in-isolation is proven; the real falsifier is whether ANY real stub converts with only
this binder. The executor MEASURES (port verbatim + whole-body `--fun`) the smallest-blocker
candidates and converts the FIRST that reaches `--fun` SUCCESS with the binder alone:
- candidates (census, review §6): `_mixin_dep_pseudo_functions` (`{nm: ty for nm, ty in params}`
  dict-comp over pairs), `_build_method_param_types_map` (`symtable.items()`), or another
  `_build_method_*_map` row. Prefer a `for a,b in <List[Tuple[str,str]]>` (case c) row — closest to
  the discharged spike.

### Refutation exit (mandatory)
If NO candidate converts end-to-end with ONLY the binder (every one carries an additional co-blocker
— string-facade, nested-def closure, Dict[str,Any] int-erasure, dict-comp-specific gap) → do NOT
land the binder standalone (an unused/co-blocked emitter branch = unused-facade, Gate C REJECT).
Instead record: binder PROVEN + banked, but consumers compound-blocked; the NEXT wall is the
narrowest co-blocker. Revert the emitter edit to clean.

## Gate battery (unchanged; supervisor owns the long planes)
verbatim mirror body; `#@ requires True/ensures True/assigns <tight>`; `--fun` SUCCESS (executor,
synchronous); whole-file Why3 proof of every changed-emission file (SUPERVISOR); corpus byte-diff 0
recomputed (SUPERVISOR); mirror-sync drift 2; ledger 3 (no new axiom/ADT/cert — the pytuple record
already exists); count strictly down from 721. If the build edits a VERIFIED emitter method, re-port
its mirror verbatim same increment.
