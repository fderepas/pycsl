# OPEN ROUTE #236 — THE `@dataclass` FIELD WHOSE `None` DEFAULT READ AS ZERO

**Status: REPAIRED (gen #36, 2026-10-15), Severity 1.** Was: OPEN (gen #36, 2026-10-15). Found by the ch10 chain agent while measuring the
Optional/defaulted-record-field seam; driver-reproduced at HEAD 50b5fa16 (rc=0, "All contracts formally proven").

## Witness (PROVED at HEAD; CPython `g(5)` returns 2)
`witnesses-r236/dataclass_none_default_reads_zero.py`:

    @dataclass
    class P:
        x: int
        k: Optional[int] = None

    #@ ensures \result == 1        <-- PROVED
    #@ assigns \nothing
    def g(c: int) -> int:
        p = P(c)
        if p.k == 0:
            return 1
        return 2

Emission: `let p = { x = c; k = 0 } in if (p.k = 0) ...`. Siblings (also PROVED at HEAD, per the agent):
`u1_optint_eq0` (`\result.k == 0`), `u2_optstr_eq0` (`Optional[str]`, `\result.name == 0`),
`u5_optlist` (`Optional[List[int]]`, `\result.items == 0`).

## Mechanism
Route #183's shape on a second channel. `Module5_IREmitter.py`'s dataclass class-body default collector
sends a `None` default to `pass` (`isinstance(_rhs145, (ast.Constant, ast.Dict, ...)): pass`, ~L3620,
comment: None is "carried by its own channel" — no channel carries it). `expressions.py::_field_default`
(~L14132) then falls through to `defaults.get(fn, 0)`: a DEFINITE `0` for an omitted `Optional[...]`
field that collapses to `int`.

## Related (agent probes)
- Explicit `P(c, None)` -> opaque `pycsl_none`, does not prove (correct).
- `name: str = "w"` omitted -> `name = 0` against a `string` field: Why3 type error (fail-closed by luck).
- `float = 2.5` -> `2` against `real`: type error (fail-closed by luck).
- Corpus: 20 class-body `= None` sites (0772-0776, 0746, 0750, 0941, 0962-0965); Dict/Set ones get a
  definite empty map.

## Repair direction
Record class-body `None` defaults in `field_none_defaults` (int -> `pycsl_none`, str -> `pycsl_none_str`);
capture class-body literal defaults faithfully (str into `field_str_defaults`, float as real) or leave the
field UNCONSTRAINED — never a wrong definite value. Agent's scratch patch:
scratchpad ch10/seam-scratch-full.patch (session scratchpad; re-derive, do not trust).

## Wider probe (executor, base 3501dd72) — "a wrong DEFINITE default" over every default channel
CPython ground truth for every row below was taken by running the witness. "refused" = Why3 type
error or pipeline refusal at base.
| shape | base | repaired |
|---|---|---|
| `@dataclass` `k: Optional[int] = None` omitted, `p.k == 0` / `\result.k == 0` (2110/2111, witness) | **PROVED** (`k = 0`) | `pycsl_none` — FAIL |
| `Optional[str] = None` (`\result.name == 0`, 2112), `Optional[List[int]] = None` (2113), `Optional[bool] = None` (`p.b == False`, 2114), `k: int = None` (2115) | **PROVED** (int carrier `0`) | `pycsl_none` — FAIL |
| `field(default=None)` (2116); keyword-only `field(default=None, kw_only=True)` (2117) | **PROVED** | `pycsl_none` — FAIL |
| `name: Optional[str] = "w"` (2118): `p.name == "w"` decided False | **PROVED** | `(any int)` — FAIL |
| `k: int = "w"` (2119); `k: Union[int, str] = "w"` (2120): `p.k == 0` | **PROVED** | `(any int)` — FAIL |
| `k: int = 2.5` (2121), `field(default=2.5)` (2122), keyword-only `field(default=2.5, kw_only=True)` (2123): truncated to 2 | **PROVED** `== 2` | `(any int)` — FAIL |
| PLAIN class `__init__(self, x, k: Optional[int] = None)` (2124), keyword-only twin (2125), `Optional[str]` (2126) | **PROVED** (route #149's `(any int)` was gated to `int`/`bool` fields; the `_union_*` field kept `0`) | `(any int)` — FAIL |
| `name: str = None` / `name: str = "w"` / `Optional[float] = None` / `float = 2.5` / tuple default | refused (ill-typed int on `string`/`real`) | `str`: faithful (`pycsl_none_str` / `"w"`); `real`/tuple: still refused |
| non-Optional `Dict`/`Set`/`List` `= None` (definite empty collection) | refused for `is None`, `== {}`/`== []`, truthiness-on-dict (type errors); `if p.items:` PROVES False — which IS CPython's answer (`None` is falsy); `len()`/`in` raise `TypeError` in CPython (outside the exception model) | unchanged (no false claim reachable) |
| `Optional[Dict]`/`Optional[Set]`/`Optional[Q]` `= None` (int carrier) | `is None` / `is not None` / `3 in p.s` not proved | `pycsl_none` |
| NamedTuple defaults (`None`, int, str, bool, module constant, `Optional[Dict]`) | refused or faithful (no false proof) | unchanged |
| plain `__init__` int/str/bool/module-constant defaults; class attributes on a plain class | faithful / refused | unchanged |
| inherited dataclass field with a `None`/str/factory default; `super().__init__` | refused (`unbound symbol 'k'`, the control too) | unchanged — see residuals |
| nested records (`q: Q = Q(3)`, `q: Q = None`, `P(c, Q(c))` with a None-default in `Q`) | refused | unchanged |
| CONTROLS: omitted `Optional[int] = None` -> `p.k is None` (2127); `name: str = None` -> `p.name is None` (2128); omitted `name: str = "w"` -> `\result.name == "w"` (2129) and through a keyword call (2130) | refused / not proved | **PROVED** (completeness gain) |
| CONTROLS: explicit `P(c, None)` -> `p.k is None` (2131); `k: int = 5`, `m: int = 2.0` -> `p.k + p.m == 7` (2132) | PROVED | PROVED |

## Repair landed (gen #36, 2026-10-15)
* Module 5 `visit_ClassDef` (mirror `\trusted`, inline, no new `self` attribute, no new `def`):
  for a `@dataclass` that SYNTHESIZES its `__init__`, the class-body defaults the collector
  `pass`ed are routed to existing channels — `None` (bare or `field(default=None)`) joins route
  #183's `field_none_defaults`; a `str` literal on a `str` field joins finding-0700's
  `field_str_defaults` (faithful); a `str` literal on any other field, and a NON-INTEGRAL float
  (incl. `-2.5`) on a non-`float` field, joins route #145's `init_unknown_fields` (`(any int)`).
* Module 5 `construction_synth._dc_default_const` (not mirrored): a non-integral float is no
  longer `int()`-truncated into a keyword-only default (route #148's rule).
* Module 6 `_call_record_constructor` (mirror `\trusted`): `_field_default`'s `str` arm answers
  `pycsl_none_str` for a `field_none_defaults` field; route #149's omitted-unknown-default gate
  also covers `_union_*` fields (emitted with the `int` carrier).

Gates (base worktree at 3501dd72): witnesses 2110-2126 PROVED at base, FAIL after on an unproved
goal; controls 2127-2132 PASS. Corpus 0 MOVED / 0 GONE / 0 APPEARED of 1485 (+23 new); pyref 0
MOVED of 2198; mirror 1 MOVED of 53 — `frontend__Module2_Parser` (`HappyProperty`'s five
`Optional[...] = None` fields `0` -> `pycsl_none` in `_contractparser___parse_happy_region`, whose
contract is `ensures true` + frame: `why3 --type-only` clean, that goal 27/27 Valid at base and
after). Soundness planes 61/61 (IR goldens unchanged); mirror sync and mirror-check green.

## Residuals
* The explicit-`__init__` `Optional[...] = None` parameter default is UNCONSTRAINED, not
  `pycsl_none`: sound, but `P(c).k is None` does not prove there (route #149's channel carries
  "unknown", not "None").
* A dataclass `Optional[float] = None` / `float = 2.5` / tuple default and a `Q`-typed `= None`
  field are still refused (ill-typed int on `real` / record); faithful `real` defaults would be a
  completeness item.
* Inheritance: a derived record does not inherit `field_none_defaults` / `field_str_defaults` /
  the class-body unknown list (`ir_resolve.apply_inheritance` merges `field_defaults` only). Every
  inherited-field read probed is refused today (`unbound function or predicate symbol 'k'`, the
  int control too), so nothing proves — but a repair that makes inherited fields readable must
  merge these channels first, or route #236 reopens through the base class.
