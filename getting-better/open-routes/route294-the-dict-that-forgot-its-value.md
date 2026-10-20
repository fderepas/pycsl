# OPEN ROUTE #294 — AN ANNOTATED dict LOCAL WHOSE FIRST ASSIGNMENT IS NOT A dict LITERAL IS LOWERED TO THE EMPTY MAP
**Status: REPAIRED (gen #37, 2026-10-20; opened the same day), Severity 1.** Originally: Found by the ch29 drain; driver-reproduced at 7569ccb7
(false_proof_hval_alias.py, false_proof_hval_alias_dictcopy.py rc=0; CPython True).
Witnesses `witnesses-r294/`: `e: Dict[str, str] = func; return "name" in e` with `ensures \result == False` proves (CPython True);
same with `Dict[str, PyVal]` and `dict(func)`; also confirmed for `Dict[str, List[int]]` and `Dict[str, Dict[str, int]]` (value
type string / seq / nested map / hval / emit_ir; NOT int). Site: `src/pycsl/module6_whyml/statements.py` `_emit_first_assign`
(~79-82): `_empty = self._dv_empty_default(nu); if _empty: val = _empty` replaces the lowered RHS before (and regardless of)
the dict-literal test. Affects ordinary user programs. Repair: use the empty base only when the RHS is a dict literal (or
{}); otherwise keep the lowered value (type-checks or fails L3-tc); census every annotated-collection first-assign path.

## REPAIR (2026-10-20, branch r294 off 339637a4)
Probe table (`pycsl.py`, rc; CPython ground truth in each corpus file's `__main__`):

| shape (claim `"name" in e` is False; CPython True) | 339637a4 | after |
|---|---|---|
| `e: Dict[str, str] = func` (3430, route `false_proof_str_alias`) | PROVED | FAIL (goal unproven) |
| `e: Dict[str, PyVal] = func` (3431, route `false_proof_hval_alias`) | PROVED | FAIL (goal unproven) |
| `e: Dict[str, PyVal] = dict(func)` (3432, route `..._dictcopy`) / `Dict[str, str]` (3433) | PROVED | REFUSED (L3-tc: `dict_1` is int-erased) |
| `e: Dict[str, List[int]] = func` (3434), `e: Dict[str, Dict[str, int]] = func` (3435) | PROVED | FAIL (goal unproven) |
| `e: Dict[str, str] = mk()` (3437), `= func if c else {}` (3438) | PROVED | REFUSED (L3-tc) |
| `a: Dict[str, str] = func; e: Dict[str, str] = a` (3439) | PROVED | FAIL (goal unproven) |
| `s: Set[str] = set(); s = func` (3442) / `s: Set[str] = func` + `s = set()` elsewhere (3443) | PROVED | REFUSED (L3-tc) |
| `e: Dict[str, str] = func.copy()` (3436), `e: Set[str] = func` (3440) — census rows | FAIL (L3-tc) | FAIL (L3-tc) |
| controls 3441: `{}`/`dict()`/literal/store for str, PyVal, List[int] values; `Set[str]` `set()` + `.add`, re-`set()` | PASS | PASS |

Rules (inline in the live emitter, no new def/field, no axiom — ledger 3; both edited methods have `\trusted`
mirror twins, the `_emit_first_assign` twin updated inline for documentation fidelity):
- `_emit_first_assign` (dict kind): the ν-typed empty base `(const (None: option ν))` replaces the lowered RHS ONLY
  when the RHS is a dict literal (the existing fold then puts its entries back on that base) or the RHS already
  lowered to the int-typed everywhere-None map `(const (None: option int))` (`dict()`, factory-form
  `defaultdict`/`Counter`/`OrderedDict` — the same empty value, re-annotated to ν). Any other RHS is KEPT: it
  type-checks as `map κ (option ν)` (`ref func`, `ref !a`) and reads go through it, or it is an L3-tc type error
  (fail-closed). Int-valued dicts were never affected (`_dv_empty_default` returns "" for ν = int).
- CENSUS sibling, `_handle_assign_stmt` `_str_set_locals` arm: an emitter-local `Set[str]` (annotated, and SOME
  assignment of it is `set()`) lowered EVERY assignment, first or re-, to `StrSet.empty ()`. Only an argument-less
  `set()` is the empty set now; any other RHS keeps its lowering (an int-erased `map int (option int)` set is an
  L3-tc error against `StrSet.set`: refused).
CENSUS of the "default replaces RHS" family (first-assign / re-assign of annotated collections):
- dict first-assign (this route) and str-set assign (sibling) — REPAIRED above.
- dict/set re-assign (`:= val`), seq-promoted list locals (`_handle_seq_assign`: literal -> `Seq.cons`, else
  `snapshot`/the seq value), array locals (`_emit_array_local_reassign`: non-literal REFUSED, route #18),
  option-tuple / pyval / record / lambda / bounded-int first-assign, ghost dict/set/list assigns: all keep the RHS.
- map-typed self-field store: repaired by route #111 (unknown RHS -> `any_map`, never the empty map).
- other RHS shapes probed after the repair, all fail-closed (L3-tc): `func.copy()` (kind `default`, `ref 0`),
  `dict(func)` / `set(func)` (int-erased `dict_1`/`set_1`), `{**func}` (str and int dict), dict comprehension (str
  and int dict). `e: Dict[str, int] = func` keeps `ref func` (unchanged; reads are faithful).
- try-body pre-declarations (`stmt_control_flow` `_handle_try_stmt`: `ref (const (None: option int))` / `ref 0`
  outer refs) are an INITIAL value overwritten by the body's own `:=` (which keeps its RHS); not this family.
Blast radius: corpus root 0 MOVED / 0 GONE / 0 APPEARED (1855 base / 1869 candidate, 14 new sources), pyref 0/0/0
(2186/2186); mirror 0 MOVED / 0 GONE / 0 APPEARED (53/53). No mover, so no M1 re-proof and no mirror proof is owed.
