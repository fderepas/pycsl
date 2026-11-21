# OPEN ROUTE #238 — `<hval> or []` REPLACES ANY NON-MAP VALUE WITH THE EMPTY MAP

**Status: REPAIRED (gen #36, 2026-10-15), Severity 1.** Repaired together with route #237.

**Was: OPEN (gen #36, 2026-10-15), Severity 1.** Found by the ch12 chain agent; driver-reproduced at HEAD
0923aa92 (rc=0 "Verification SUCCESS").

## Witness (PROVED at HEAD; CPython `g({"args": [1, 2]})` = 2)
`witnesses-r238/or_list.py`: `a = d.get("args", []) or []`; `return len(a)` with `ensures \result == 0`.

## Mechanism
`expressions.py` `_recognize_pyval_or_default` (comment ~L5241) emits
`match v with HMap _ -> v | _ -> HMap PNil`: a truthy list / string / int is discarded.

## Repair direction
Faithful Python `or`: keep `v` when it is truthy (non-empty HArr/HMap/HStr, non-zero HInt, ...), else the
default; or opaque when truthiness of the shape is not modelled. Never a definite value for a truthy operand.

## Probe table (base 3deece44 -> repaired)
| shape | base | repaired | corpus |
|---|---|---|---|
| `len(d.get("args", []) or [])` == 0 (false) | PROVED | FAIL (undecided) | 2142 |
| `isinstance(d.get("k", {}) or {}, dict)` (false) | PROVED | FAIL | 2143 |
| hval-local `x.get("j", 5) == 0` on a missing key (false; default was the empty map, outer `{}` default `HInt 0`) | PROVED | FAIL | 2148 |
| CONTROL `{"args": [1, 2]}`: `or []` keeps the list, len 2 | FAIL | PASS | 2152 |
| CONTROL "args" absent: `or []` is empty, len 0 | PASS | PASS | 2154 |
| CONTROL "k"/"s" absent: `d.get("k", [])` is a list, `d.get("s", "")` a str | FAIL (`[]` -> `HInt 0`; `""` ill-typed) | PASS | 2157 |
| `d.get("k", []) and []` | ill-typed (refused) | unchanged (refused) | — |

## Repair landed (gen #36, 2026-10-15)
`expressions.py::_recognize_pyval_or_default`: `v or D` is now
`let v_or = v in match v_or with HArr HNil -> D | HArr _ -> v_or | HMap PNil -> D | HMap _ -> v_or
| HInt i -> if i <> 0 then v_or else D | HStr _ -> if hval_truthy v_or then v_or else D | HNode _ ->
v_or end`, with D the faithful carrier of its own literal (`_pyval_wrap`: `{}` -> `HMap PNil`, `[]`
-> `HArr HNil`). Python truthiness per constructor, never a discarded truthy operand. The selector is
NOT `hval_truthy` for the decidable carriers: its HStr arm calls the program `val hpairs_key_eq`, so
the whole function is logic-opaque (measured: `goal hval_truthy (HArr (HCons (HInt 1) HNil))` times
out) and the 2152 control would be undecided. Missing-key defaults (`_lower_dict_get_call`):
`d.get(k, D)` on a `Dict[str, PyVal]` (param/local, self-field, hval local) answers `_pyval_wrap(D)`
— `{}`/`[]` were the `HInt 0` sentinel (param/local) or the empty MAP whatever D was (hval local),
`""` was an ill-typed raw literal; 1-arg `d.get(k)` answers `HInt pycsl_none` (was `HInt 0`, so
`d.get("k") == 0` proved with "k" absent — witness 2144). See route #237 for the shared gates and
residuals. Ledger 3; no new axiom, refusal or raise.

## Residuals
- `and` on an hval (`x and []`) and `x is None` / `type(x) == dict` remain REFUSED (ill-typed), not
  modelled.
- The hval-local `.get` on a NON-map receiver answers D (Python raises `AttributeError` for a
  str/int/list receiver, and an `HNode` IR dict would answer its real entry) — a placeholder on a
  raising path / mirror-only carrier, not a decided false value for a dict receiver.
