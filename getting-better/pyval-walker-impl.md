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

## §OUTCOME-C1 — 2026-07-24 driver run: LIST-accumulator carrier BUILT + 1 conversion (940 → 939)

**Verdict: the C1 `List[str]`-accumulator carrier is BUILT, spike-PASSED, and converts
`from_sexp._walk_modpath` (the ONE C1 stub reachable by the List carrier ALONE). The other
3 C1 stubs stay [COST/SCALE] behind a distinct, precisely-located wall — CROSS-FUNCTION
CALLS + WhyML forward-reference/mutual-rec ordering (renamed C1b below).**

### GATE-S census (lesson p) — reachable-ALONE sub-cluster size = 1
Of the 4 C1 candidates, exactly ONE is reachable by the List-accumulator carrier ALONE:
- `_walk_modpath` — **self-recursion only, NO cross-function call, no `[-1]`.** REACHABLE. ✓
- `_walk_kername` — calls `_walk_modpath` (a helper that must carry a `pyval` param). NOT alone.
- `_find_kername_components` — calls `_walk_kername` + self. NOT alone.
- `_full_const_path` — calls `_find_kername_components`. NOT alone.
The 3 non-alone stubs are all blocked by **C1b** (a cross-function call to a sibling that must
itself be a `pyval`→`list string` function), AND by WhyML **forward-reference ordering**: source
order is `_walk_kername`(1st)→`_walk_modpath`(2nd), so a converted `_walk_kername` forward-refs
`_walk_modpath` (WhyML `let` is sequential; needs a `let rec … with` mutual group the per-function
recognizer path does not emit). Distinct feature, not the List carrier — deferred with a measured
reason, not speculatively built.

### Make-or-break spike — PASSED on `_walk_modpath` (CORRECTNESS)
The spike falsifier was NOT provability of the list-build (that typechecks trivially) but
**TERMINATION of the TREE self-recursion** `_walk_modpath(mp[1])`. Hand-lowered `_walk_modpath`
to a `list string` accumulator (`app`/`rev` + a spine fold): Why3 **typechecks** the accumulator
shape (L3-tc ✓), the inner spine fold's `variant { l }` is Valid, but the outer
`variant { pv_size v_mp }` **times out** — Why3 cannot prove `pv_size (pnth v_mp 1) < pv_size v_mp`
unaided. Fix (the DICT-analog `size_dict_mem` cert lemma already exists): an **axiom-free per-function
`let rec lemma {n}__size_nthl`** (`0 <= i < lenl l -> pv_size (nthl l i) <= size_list l`, the recursion
IS the induction, calling the certified `size_pos`/`size_list_nonneg`). With it, **Alt-Ergo (the
pipeline's FIRST prover) proves the whole `_walk_modpath'vc` unsplit in 0.14 s** (z3 OOMs — moot,
Alt-Ergo is tried first). NO new axiom, ledger stays 3. Real pipeline: `--fun _walk_modpath` **SUCCESS**,
whole-file `from_sexp.py` proof **SUCCESS**.
**MUTATION TEST (Gate C, decisive):** `"MPfile"` → `"MPZZZ"` in the body → the emitted `.mlw`'s
`pystr_eq … "MPfile"` becomes `… "MPZZZ"`. Non-facade.

### What was BUILT (all in `src/pycsl`, NOT the mirror → 0 new stubs, net +1)
- **`recognize_pyval_list_walker` + `emit_pyval_list_walker_group`** (`generic_fold.py`) — a
  CPS/state-passing STRUCTURAL translator threading the current `list string` value of every
  in-scope accumulator. Fragment: `<acc>=[]`; `<var>=vref` (pyval bind); `<acc>.append(strexpr)`;
  `<acc>.extend(listexpr)`; `if/else`; `for x in vref` (single-accumulator fold); `return <acc>`/
  `return []`; `listexpr ::= <acc> | reversed(<acc>) | <selfname>(vref)`; `test` += bare-`vref`
  tuple truthiness (`plen>0`). Fail-closed `_PVWBail` → None.
- **inline TOTAL list ops** `{n}__app` (list append) + `{n}__rev`/`{n}__revacc` (reverse) — DEFINED
  `let rec function`s, self-contained: **NO preamble `use list.Append/Reverse`** → zero corpus byte-diff.
- **inline TOTAL projectors** `{n}__nthl/pnth/lenl/plen/atom` (reused from the string walker).
- **axiom-free `{n}__size_nthl` lemma** — emitted ONLY when the body is tree-self-recursive (ledger 3).
- **dispatch** (`functions.py`) after the string-walker block; **needs_pydict gate** (`preamble.py`
  `_scan_preamble_needs`, a `\trusted` mirror stub → no §10.4 re-port) pulls the pyval theory (+
  `use list.List`) into scope when the recognizer fires — REQUIRED for a standalone fixture (in the
  mirror `_walk_modpath` piggybacked on `_binder_name`'s already-pulled theory).

### Gate battery (driver-verified fresh)
- count 940 → **939** (`_walk_modpath` un-`\trusted`); ledger **3** (size lemma is `let rec lemma`
  PROVEN by Alt-Ergo; app/rev/projectors DEFINED; no cert/allowlist/formal-semantics touched).
- `--fun _walk_modpath` **SUCCESS**; **whole-file** `from_sexp.py` proof **SUCCESS**; L3-tc ✓.
- **corpus byte-diff 0** (789 common == 789, mine vs detached-HEAD worktree with `.venv` symlinked;
  only the NEW `0943_pyval_list_walker.mlw` is mine-only). The list recognizer does NOT over-fire.
- **suite-mirror byte-diff 0** (34 proven-suite mirrors byte-identical HEAD vs mine, both BEFORE and
  AFTER the preamble edit ⇒ the self-annotation proof suite is provably unaffected).
- vacuity `--emit from_sexp` exit 0: 0 input-blind, no NEW erasure (the 3 KNOWN unchanged;
  `_walk_modpath` reads its param).
- mirror-check **52/52**; drift **2 == HEAD** (`_walk_modpath` in sync = verbatim port; the 2
  pre-existing `_handle_var_expr`/`_handle_for_stmt` still-blocked).
- reference fixture (`git add -f`): `0943_pyval_list_walker.py` — a standalone `walk_path` tree
  walker that fires the recognizer, exercises `.append`/`.extend`/`reversed`/for-fold + the tree
  self-recursion size lemma, and PROVES (regression lock). No evil-twin (ensures True, no oracle to
  collapse to; mutation test + vacuity gate are the non-vacuity lock).

### §RESIDUAL-C1b — the other 3 C1 stubs ([COST/SCALE], cross-call ordering)
`_walk_kername`/`_find_kername_components`/`_full_const_path` need the List carrier PLUS: (a) a
cross-function call to a sibling that is itself a converted `pyval`→`list string` function (a
trusted `val` sibling has an `int` param → type mismatch, the C2 wall); (b) WhyML forward-reference
resolution — either a `let rec … with` mutual-group emission from the per-function recognizer path, or
dependency-order emission. Both are bounded (no 4th axiom, Why3 accepts the carrier) but distinct
builds. The List carrier is the reusable foundation; C1b is the next increment when authorized.

## §OUTCOME-C1b — 2026-07-24 driver run: C1b BUILT + 3 conversions (939 → 936)

**Verdict: C1b is BUILT and converts ALL 3 remaining C1 stubs (`_walk_kername`,
`_find_kername_components`, `_full_const_path`). Count 939 → 936. Ledger 3 (no new axiom).**

### GATE-S census — CORRECTION to the C1b premise
The residual predicted a `let rec … with` MUTUAL group for a forward-reference/mutual-recursion
wall. The census found the cluster is a **DAG**, not a mutual-recursion cycle:
`_find_kername_components`→`_walk_kername`→`_walk_modpath` (each self-recursive), `_full_const_path`
→`_find_kername_components`. No back-edge between distinct functions ⇒ each is its own SCC. The
EXISTING SCC topological ordering (`scc.py`, callees-before-callers, driven by `find_calls_in_ir`
body edges) ALREADY emits `_walk_modpath` before `_walk_kername` etc., so **no mutual-group emission
is needed** — the real blockers were (i) cross-function sibling-walker CALLS in the walker fragment,
and (ii) for `_find_kername_components`, a SEARCH-loop shape (self-call on a spine ELEMENT, not
`p[i]`). Reachable sub-cluster size = **3** (all, sequenced by the DAG dependency).

### What was BUILT (two carriers, both in `src/pycsl`, ledger 3)
- **Cross-call carrier** (`_pvl_listexpr` sibling case + `recognize_pyval_list_walker(func,
  sibling_walkers)` + `compute_pyval_list_walker_names` fixpoint + Module6 wiring + `functions.py`
  dispatch). A walker may call a sibling recognized `pyval`→`list string` walker; SCC ordering places
  the callee first. Converts `_walk_kername` (cross-calls `_walk_modpath`) ALONE.
- **Search catamorphism** (`recognize_pyval_list_search` / `emit_pyval_list_search_group`) — the
  `_find_kername_components` tree-search shape emitted as the certified mutual
  `let rec {n}(v) variant { pv_size v } with {n}__list(l) variant { size_list l }` (the
  `emit_bool_multiway_group` precedent). Cross-decreasing structural measures discharge termination
  AUTOMATICALLY — **spike: 24 VCs Valid under Alt-Ergo, 0 non-valid, NO new axiom**. Plus the C1
  Return handler generalized to `return <listexpr>` (a cross-call) for `_full_const_path`.

### Gate battery (driver-verified fresh, per conversion)
- count 939 → **936** (`_walk_kername` 938, `_find_kername_components` 937, `_full_const_path` 936);
  ledger **3** (projectors/list-ops DEFINED; search-group termination is the certified pyval
  `pv_size`/`size_list` cross-variant; no cert/allowlist/formal-semantics touched).
- `--fun` each **SUCCESS**; **whole-file** `from_sexp.py` proof **SUCCESS** (Valid); L3-tc ✓.
- **MUTATION TEST** (decisive) on both new emitters: `"KerName"`→`"KerZZZZ"`/`"KerQQQQ"` in the body
  changes the emitted `.mlw`'s `pystr_eq … "…"`. Non-facade (no int-hash/oracle to hide behind).
- **corpus byte-diff 0** (790 common == 790, detached-HEAD baseline; only the NEW fixtures 0944/0945
  are mine-only). Both carriers fire ONLY on the exact shapes → byte-inert on real programs.
- mirror-check **52/52**; drift **2 == HEAD** (both new bodies verbatim = in sync; the 2 pre-existing
  `_handle_var_expr`/`_handle_for_stmt` still-blocked).
- vacuity `--emit from_sexp` exit 0: 0 input-blind, no NEW erasure (both read their params).
- fixtures (`git add -f`): `0944_pyval_list_walker_crosscall.py` (cross-call witness),
  `0945_pyval_list_search.py` (search-catamorphism witness) — both PROVE (regression locks).

### §RESIDUAL-after-C1b — the from_sexp cluster remaining ([COST], C2/C3)
`_const_name` / `_ind_short_name` = C2 (call the `List[str]` helper + index `[-1]` neg-from-end;
their return is `Optional[str]` not `List[str]`). `_construct_indices` / `_find_construct_idx` /
`_flatten_tuples` = C3 (tuple/int result algebras). Bounded, distinct builds; not this run.

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
