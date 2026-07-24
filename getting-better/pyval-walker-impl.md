# pyval-walker-impl.md — the general value-returning pyval string walker (backlog item 3)

The §10.3 "structure-returning `Any`-walker" class — a string-RETURNING catamorphism over a
heterogeneous nested-tuple/list param (`Dict[str,Any]`/sexp spine), modeled on the certified
`pyval` ADT. The BOOL-existence recognizer family cannot model these (they return a value BUILT
from the tree, not a bool). This build lands the walker, PROVEN and NON-FACADE, and converts the
first stub of the `from_sexp` sexp-carrier cluster.

## §OUTCOME — 2026-07-24 driver run: BUILT + 1 conversion (count 941 → 940), residual COST/SCALE

**Verdict: the value-returning pyval walker is BUILT, spike-PASSED, and lands `_binder_name`
(from_sexp) as the first conversion. The prior [COST/SCALE] "no bounded non-facade entry"
(sexp-carrier-impl.md §OUTCOME-2) is SUPERSEDED for the self-contained `Optional[str]` fold shape:
there IS a bounded, general, non-facade entry — it is now in-tree. The residual (the rest of the
cluster) stays [COST/SCALE] with the additional carriers precisely enumerated below.**

### GATE-S census (lesson p)
Single structured-param, str-returning `\trusted` stubs = 15. The pyval-value-returning-walker-
reachable cluster is the **from_sexp sexp-carrier** (7 stubs: `_walk_kername`, `_walk_modpath`,
`_const_name`, `_full_const_path`, `_find_kername_components`, `_ind_short_name`, `_binder_name`).
The 3 other pyval-shaped candidates are NOT this class: `_type_str` (flat `node.get("type")` dict
read + sibling call — not a tuple-index fold), `_tag_of_value` (self-state `_current_symbol_table`
+ `sum(ord c)` int-hash), `_infer_return_value_type` (self-state / call). So the cluster is the
from_sexp 7.

### Make-or-break spike — PASSED on `_binder_name` (cleanest: self-contained, no helper call)
Ported the live body VERBATIM into the mirror; built the recognizer+emitter+projectors; then
`--fun`/whole-file proof. The emitted body is a real fold over the pyval spine (excerpt):
```
let _binder_name (v_binder_annot: pyval) : _union__binder_name_2 =
  if not (is_plist v_binder_annot) then Arm_2_None
  else (let rec _binder_name__loop0 (l: list pyval) : _union__binder_name_2 variant { l }
        = match l with Nil -> Arm_2_None
          | Cons v_field rest ->
              if is_plist v_field && _binder_name__plen v_field >= 2
                 && pystr_eq (_binder_name__atom (_binder_name__pnth v_field 0)) "binder_name"
              then let v_val = _binder_name__pnth v_field 1 in
                   if pystr_eq (_binder_name__atom v_val) "Anonymous" then Arm_2_None
                   else if is_plist v_val && pystr_eq (…pnth v_val 0…) "Name" && …plen v_val >= 2
                   then let v_inner = …pnth v_val 1 in
                        if …pnth v_inner 0 = "Id" && …plen v_inner >= 2
                        then Arm_2_0 (_binder_name__atom (_binder_name__pnth v_inner 1))
                        else _binder_name__loop0 rest
                   else _binder_name__loop0 rest
              else _binder_name__loop0 rest end
        in _binder_name__loop0 (match v_binder_annot with PList xs -> xs | _ -> Nil end))
```
Reads the REAL spine via `pnth`/`atom`/`plen`, compares REAL string literals, returns the union
arms `Arm_2_0 (atom …)` / `Arm_2_None`. NO int-hash, NO `any_1`, NO `last_atom` sidestep.
**MUTATION TEST (Gate C, decisive):** `"binder_name"` → `"binder_XXXX"` in the body → the emitted
`.mlw`'s `pystr_eq … "binder_name"` changes to `… "binder_XXXX"`. Non-facade. There is no oracle/
int-hash erasure to hide behind, so the mutation test IS decisive here (contrast wall-lessons (l)).

### What was BUILT (all in `src/pycsl`, NOT the mirror → 0 new stubs, net +1)
- **3 inline TOTAL projectors** `{n}__pnth` / `{n}__plen` / `{n}__atom` over the certified pyval
  ADT (PList/PStr), emitted per-recognized-function (the `emit_frt_group` `__llen` precedent). They
  are `let function` / `let rec function` — **DEFINED, not axiomatized**; termination is the
  structural `list pyval` variant. The pyval `pv_size`/`size_pos` cert already covers the measure,
  so **ledger stays 3** (no new certificate, no `Phase2*`/`.lean`, no allowlist edit).
- **`recognize_pyval_string_walker` + `emit_pyval_string_walker_group`** (`generic_fold.py`) — a
  STRUCTURAL translator (not a shape matcher) for the fragment: `not`/`and`/`or`;
  `isinstance(vref, tuple|list|dict|str)`; `len(vref) OP <int>`; `vref == "<lit>"`; positional
  `vref[<int>]`; `<var> = vref`; `if/else`; `for <var> in vref` (fold w/ early return); `return
  None`/`return <strexpr>`. Fail-closed: any node outside the fragment raises `_PVWBail` → recognizer
  returns None (precision-over-recall). The "param-annotation→pyval hook" is intrinsic: the emit
  group declares the param `(… : pyval)` (like `emit_frt_group`).
- **dispatch** (`functions.py`) — resolves the synthesized 2-arm `Optional[str]` union
  (`Arm_?_0 string` + `Arm_?_None`) from `self._variant_types` and passes the ctor names.
- **needs_pydict gate** (`preamble.py`) — pulls the pyval theory into scope when the recognizer fires.

### Gate battery (driver-verified fresh)
- count 941 → **940** (`_binder_name` un-`\trusted`); ledger **3** (no cert/allowlist/formal-semantics
  touched; projectors DEFINED not axiomatized).
- `--fun _binder_name` **SUCCESS**; **whole-file** proof of `from_sexp.py` **SUCCESS** (Valid).
- L3-tc ✓ (whole file). Vacuity `--emit` exit 0: **0 input-blind**, no NEW erasure (`_binder_name`
  reads its param; the 3 KNOWN erasures unchanged).
- **corpus byte-diff 0** (788 == 788, mine vs detached-HEAD worktree with `.venv` symlinked, identical).
- **mirror byte-diff: ONLY `from_sexp.mlw` differs** across all 52 mirrors → the recognizer does not
  over-fire; every other mirror `.mlw` is byte-identical to HEAD ⇒ the self-annotation proof suite is
  provably unaffected.
- mirror-check **52/52**; drift **2 == HEAD** (the 2 pre-existing STILL-BLOCKED `_handle_var_expr` /
  `_handle_for_stmt`; no new drift).
- reference fixture (`git add -f`): `0942_pyval_string_walker.py` — a standalone POSITIVE witness
  that fires the recognizer and PROVES (regression lock; a facade regression changes its emission /
  breaks its proof). No evil-twin: the recognizer forces `ensures True` (no postcondition to refute)
  and emits no oracle to collapse to, so the mutation test + vacuity gate are the non-vacuity lock.

## §RESIDUAL — the rest of the from_sexp cluster ([COST/SCALE], carriers enumerated)
The walker CURRENTLY reaches exactly `_binder_name` (self-contained `Optional[str]` fold). The other
6 need distinct, still-unbuilt carriers (each a real feature, not a facade):
- **C1 — `List[str]` (`array string`/`seq string`) accumulator model** (`.append`/`.extend`/
  `reversed` + for-over-slist): `_walk_kername`, `_walk_modpath`, `_find_kername_components`,
  `_full_const_path`. These RETURN `List[str]`, not the `Optional[str]` union — a second value model
  composed with the pyval walk (BLOCKER 2 of sexp-carrier-impl.md). The walker's return path handles
  ONE string, not a built list.
- **C2 — param-annotation→pyval hook for a TRUSTED helper** (so `_find_kername_components` can carry
  a `pyval` param and return `array string` while STAYING `\trusted`) + **negative-index-from-end**
  (`parts[-1]`): `_const_name`, `_ind_short_name`. Their own bodies are clean of the accumulator, but
  call the `List[str]` helper and index `[-1]`. Converting them needs EITHER C1 (convert the helper)
  OR a real annotation→pyval-param mechanism (the current hook is usage-inferred; a trusted stub has
  no usage). This is the one genuinely-new "hook" the target named; `_binder_name` did not need it
  (self-contained), so it is deferred with a measured reason rather than speculatively built.
- **C3 — tuple/int returns**: `_construct_indices` (`Optional[Tuple[str,int]]`), `_find_construct_idx`
  (`Optional[int]` + `int(...)`), `_flatten_tuples` (`List[Any]`). Different result algebras.

Each C1/C2/C3 is a bounded feature the funded window CAN pay (not a correctness wall — no 4th axiom,
Why3 accepts the pyval carrier, the projectors are total). They are simply distinct builds; this run
banked the core walker + C-free conversion and the enumerated residual. The walker is the reusable
foundation all three extend.
