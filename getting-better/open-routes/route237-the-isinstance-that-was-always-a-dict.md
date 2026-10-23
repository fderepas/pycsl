# OPEN ROUTE #237 — `isinstance(<hval>, dict)` IS THE CONSTANT `true`

**Status: REPAIRED (gen #36, 2026-10-15), Severity 1.** Repaired together with route #238 (same hval
value-model cluster).

**Was: OPEN (gen #36, 2026-10-15), Severity 1.** Found by the ch12 chain agent (asked to check exactly this
before building an hval seam); driver-reproduced at HEAD 0923aa92: both witnesses rc=0 "Verification SUCCESS".

## Witnesses (PROVED at HEAD)
- `witnesses-r237/isinst_dict.py`: `x = d.get("k", {})` on `d: Dict[str, PyVal]`; `if isinstance(x, dict): return 1`
  / `return 0` with `ensures \result == 1`. CPython `f({"k": "s"})` = 0.
- `witnesses-r237/notdict.py`: the negated form; CPython `h({"k": 5})` = 0.
Emission: `if true then raise (Return 1) ...`.

## Mechanism
`src/pycsl/module6_whyml/expressions.py` ~L11396 (the "union/match cluster" isinstance branch, 38a46208):
an hval subject "IS a Python dict" — false: an hval is `HStr | HInt | HArr | HNode | HMap ...`. Any
`x = d.get(...)` on a `Dict[str, PyVal]` is a pyval local, so ordinary user code reaches it.

## Repair direction
Lower `isinstance(<hval>, dict)` to a constructor test (`match x with HMap _ -> true | _ -> false end`), and
`isinstance(<hval>, str|int|list)` likewise, or opaque — never a constant. Note the missing-key default
`d.get("k", {})` is emitted `HInt 0` (should be the empty map) — becomes observable once isinstance is
faithful. Mirror impact: `stmt_control_flow::_match_subject_union_info` uses `not isinstance(subj, dict)`
(ensures True) -> owes a whole-file re-proof. Agent's axiom-free spike: ch12 scratch `mlwspike/hval_isinst_streq.mlw`.

## Probe table (base 3deece44 -> repaired; all probes `Dict[str, PyVal]`, `PyVal = Any`)
| shape | base | repaired | corpus |
|---|---|---|---|
| `isinstance(d.get("k", {}), dict)`, `\result == 1` (false) | PROVED (`if true`) | FAIL (undecided) | 2140 |
| `not isinstance(x, dict)` early return (false) | PROVED | FAIL | 2141 |
| `x = d.get("k", {}) or {}; isinstance(x, dict)` (false) | PROVED | FAIL | 2143 |
| `{"a": 5}` read, `isinstance(x, dict)` (false) | PROVED | FAIL | 2147 |
| `{"a": "s"}.get("a") == 0` (false; `hint_of` read 0) | PROVED | FAIL | 2145 |
| `d.get("k") == 0` with "k" absent (false; arm was `HInt 0`) | PROVED | FAIL | 2144 |
| `len(x)` of `{"z": 1}` read == 0 (false; `hval_len` counts HArr only) | PROVED | FAIL | 2146 |
| `isinstance(x, (dict, list))` on arbitrary `d` | FAIL (`isinstance_op 0 0`) | FAIL | — |
| `isinstance(x, str)` / `(.., int)` / `(.., list)` on arbitrary `d` | FAIL (`typeof_op 120`, name-keyed) | FAIL | — |
| CONTROL known dict `isinstance(x, dict)` | PASS | PASS | 2150 |
| CONTROL missing key `d.get("k", {})` is a dict | PASS (constant) | PASS (`HMap PNil`) | 2151 |
| CONTROL known str `isinstance(x, (str, list))` | FAIL | PASS | 2153 |
| CONTROL known `{"a": 5}.get("a") == 5` | PASS | PASS | 2155 |
| CONTROL known list is NOT a dict | FAIL | PASS | 2156 |
| CONTROL `isinstance({"a": 5} read, int)` | FAIL | FAIL — undecidable BY DESIGN (HInt is the erased carrier) | — |
| `type(x) == dict`, `x is None`, `x is not None`, `x == ""`, `x and []` on hval | ill-typed (refused, L3-tc) | unchanged (refused) | — |

## Repair landed (gen #36, 2026-10-15)
`src/pycsl/module6_whyml/expressions.py` (live; the mirror twins of `_handle_isinstance`,
`_handle_binop`, `_handle_len_call` are `\trusted`; `_lower_dict_get_call` /
`_recognize_pyval_or_default` have no mirror twin — sync check stays OK):
- `_handle_isinstance`: the constant-`true` pyval arm is replaced by the hval CONSTRUCTOR
  DISCRIMINANT for ANY pyval subject (`_expr_is_pyval`: locals, `.get` reads), bare class or tuple of
  classes: HMap/HNode decide `dict`, HStr `str`, HArr `list` (positively tagged by `_pyval_wrap`:
  only a dict literal builds HMap, a list literal HArr, a string-typed value HStr); the erased
  carrier `HInt` (int, bool `HInt 1`, None `HInt pycsl_none`, tuple `HInt (any int)`) answers every
  test OPAQUELY — `(any bool)`, a fresh value per evaluation (not a function of the hval, so `True`
  and `1` are never forced alike); `object` is true; an unknown class (user class, ABC, subclass)
  is opaque on every arm. In a spec the opaque answer is the uninterpreted logic
  `hval_isinst_opaque` (no postcondition).
- `hval == <int>` (`_handle_binop`): `hint_of v = n` projected every non-int to 0; now
  `match v with HInt i -> i = n | _ -> false`.
- `len(<hval local>)` (`_handle_len_call`): HArr keeps `hval_len`; any other carrier is the
  uninterpreted `hval_len_other` (it read 0).
- Missing-key defaults (with route #238): `d.get(k, D)` answers `_pyval_wrap(D)`; 1-arg
  `d.get(k)` answers `HInt pycsl_none` (route #44's opaque None, the spelling `_pyval_wrap` gives a
  literal `None`) — param/local dicts, `Dict[str, PyVal]` self-fields, hval locals.
No new axiom: `hval_isinst_opaque`, `hval_len_other`, `pycsl_none` are `val function`s without
postcondition; `proof_axiom_allowlist` untouched; ledger stays 3. No new refusal or raise.

## Gates
Corpus byte-diff vs fresh 3deece44 baseline: root 1485/1502 .mlw, 0 MOVED / 0 GONE / 0 APPEARED
(17 new sources = 2140-2148, 2150-2157); pyref 2198/2198, 0 MOVED. Mirror: 6 MOVED
(`frontend/Module5_IREmitter`, `module6_whyml/{expressions,functions,statements,stmt_control_flow,
types}`), every hunk one of the intended corrections above, each `why3 --type-only` clean; the
14 functions holding a moved line were re-proved per-function (`why3 prove -a split_vc -P z3 -t 30
-G <fn>'vc`), 0 non-Valid: types/statements `_field_type_for`+`_field_type_of`, stmt_control_flow
`_match_subject_union_info`, `_union_ctor_for_arm_tag`, `_maybe_inject_union_return`,
`_try_union_is_none_match`, Module5 `_collect_type_params`, expressions `_union_none_ctor_for`,
`_namedtuple_positional_access`, `_typeddict_record_literal`, functions `_build_param_list`,
`_compute_return_type`, `_refine_tuple_return_type`; whole-file re-proofs of the six giants are
queued to the driver. Soundness planes 61/61 after deleting the now-stale
`check-type-keyed-constant-answers` baseline row `(_handle_isinstance, _pyval_locals, true)` (the
row that justified this bug: "an hval subject IS a Python dict"). Sync + mirror-check rc=0. Ledger 3.

## Residuals
- **None / 0 conflation under HInt** (pre-existing route #44 design, now the only way to correlate):
  `pycsl_none` is an int, so "not dict/str/list AND falsy" lets a prover conclude `x == 0` for an
  hval that is Python `None`. Contrived (needs every type test negated plus a truthiness test);
  a faithful fix needs an `HNone` constructor in the certified hval ADT (Phase2f cert change).
- **Name-keyed `typeof_op <hash(name)>`** for `isinstance` on a NON-pyval `Any` subject: two values
  bound to the same variable name share one term (reassignment correlates). Not hval; not probed to
  a proved false claim here — owed a probe.
- **Mirror-gated hval string compare** `str_eq_op (hstr_of v) s` (`_compute_return_type` and
  `ls and rs` paths) still reads a non-string carrier as `""`; user code reaching it is refused
  (ill-typed, probe p26), so only the self-annotation mirror sees it.
- **hval structural `=`** (`d.get("a") == d.get("b")`) is refused today (ill-typed); if it ever
  type-checks, HMap assoc-list ORDER would make equal dicts unequal.
