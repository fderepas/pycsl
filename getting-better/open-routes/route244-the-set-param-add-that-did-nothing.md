# OPEN ROUTE #244 — `s.add(x)` ON A SET PARAMETER IS A NO-OP UNDER `@mutable_state`

**Status: REPAIRED (gen #36, 2026-10-16), Severity 1.** Repaired together with route #243 (callee: a
faithful local shadow; caller: fail-closed refusal; no new axiom, ledger 3).

**Was: OPEN (gen #36, 2026-10-16), Severity 1.** Found by the ch16 chain agent; driver-reproduced at HEAD
4b894167 (rc=0 "Verification SUCCESS"; CPython `C().c()` = True, claim `\result == False`).

## Witness
`witnesses-r244/set_param_add_is_noop.py`: `m(self, s: Set[int])` does `s.add(1)` under `assigns \nothing`;
caller `c()`: `s = set(); s.add(2); self.m(s); return 1 in s` proves `\result == False`.

## Mechanism
`statements.py`'s "sound no-op" arm lowers an in-place mutator on a set PARAMETER (inside a `@mutable_state`
class) to nothing; the callee's frame says `\nothing`, so the caller keeps its pre-call value of `s`.

## Repair direction
Refuse an in-place mutation of a parameter's collection (caller-visible side effect) unless the frame can
express it (a by-reference carrier / caller-visible `writes`); never a silent no-op.

## Probe table (base cdac19a6 -> repaired)
| shape | base | repaired | corpus |
|---|---|---|---|
| witness: caller passes local `s`, callee `s.add(1)`, caller reads `1 in s` | PROVED | REFUSED (M, at the call) | 2290 |
| callee reads its own param after `s.add(1)` (`\result == False`) | PROVED | FAIL (shadow sees the add) | 2291 |
| caller forwards its own param, reads it after | PROVED | REFUSED (M) | 2292 |
| `s.discard(1)` in the callee, caller reads | PROVED | REFUSED (M) | 2293 |
| `s.remove(1)` in the callee, caller reads | PROVED | REFUSED (M) | 2294 |
| module-level caller `c.m(s)` (same file; the cross-file spelling was measured too) | PROVED | REFUSED (M) | 2295 |
| CONTROL callee `s.add(1); return 1 in s` (`\result == True`) | FAIL | PASS (faithful) | 2413 |
| CONTROL caller passes a fresh single-use set | PASS | PASS | 2414 |
| `d[k] = v`, `d.pop(k)`, `s.clear()` on a param; `xs.append` on a list param (all @mutable_state) | refused | refused (unchanged) | — |

## Repair landed (gen #36, 2026-10-16)
* `statements.py::_handle_expr_stmt`: the `@mutable_state` "sound no-op" arm
  (typed-ir-for-b-ceiling.md §13) is DELETED. Anything still reaching that point is refused
  (`_reject_param_collection_mutation`) or hits the in-place-mutator refusal — never erased.
* `functions.py::_reset_function_state` (CALLEE): a set/dict formal of a `@mutable_state` method
  mutated by `.add`/`.discard`/`.remove` joins `_dict_locals` + `local_refs`, so `_emit_body_code`
  binds `let s = ref s in` and the mutator lowers like a local's (`s := map_update_some !s x 0`).
  A usage-inferred κ = string is dropped for the shadow (a method's set param stays `map int`).
  The contract-named guards (#19/#62/#71) stay: a contract's `s` is the ENTRY value.
* `functions.py::_reset_function_state` (CALLER): the route #243 rule's MUTATING slots (seeded by the
  shadowed formals, closed under forwarding over the whole unit, imported bodies included): an
  argument there must be fresh or single-use, unconditionally (`PYCSL-WHYML-COLLECTION-ALIAS`).
* Other "sound no-op" arms checked: dict-param `d[k] = v` / `del d[k]` were already refused (WL-05);
  `pop`/`clear`/`update`/`setdefault` on a param hit the in-place-mutator refusal; list-param
  `append` is refused; standalone FUNCTIONS have the caller-visible by-ref model (WL-05b). The
  `<emit_ir>[k] = v` no-op (cf6 M1.4, statements.py) writes an immutable reflected value and is
  not a dict/set.

## Blast radius
* Corpus: 1146 (route #62 positive control) and 1172 (route #71 positive control) MOVED — their
  bodies now carry the real update on the shadow; both still PROVE (docstrings annotated).
* Mirror: 3 files MOVED (`module6_whyml/{expressions,statements,stmt_control_flow}`), the four
  verified methods that used the no-op (`_handle_named_expr_expr`, `_emit_new_ghost_ref`,
  `_handle_seq_assign`, `_handle_try_stmt`); `--type-only` clean, and each re-PROVES with
  `pycsl.py --fun <method>` (its contract, every callee assumed). The try-handler's loop
  (`if v not in declared_refs: ... declared_refs.add(v)`) was a stale-read the no-op made unsound
  in the verified mirror itself; it is now faithful.

## Residuals
* None known for the mutator arms. The shadow is callee-local by design: the caller-visible effect
  is not modelled, it is refused unless the caller cannot observe it.
