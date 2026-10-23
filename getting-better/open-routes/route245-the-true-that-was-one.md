# OPEN ROUTE #245 — IN A CONTRACT, AN hval `True` AND `1` ARE THE SAME VALUE, SO `isinstance(_, bool)` AGREES

**Status: REPAIRED (gen #36, 2026-10-16; opened the same day), Severity 1.** Recorded as a residual by the #242 repair executor;
driver-reproduced at HEAD 7b823836 (rc=0 "Verification SUCCESS").

## Witness
`witnesses-r245/hval_true_is_one_in_contract.py`: `f(d: Dict[str, PyVal])` with
`requires d["a"] == d["b"]` and `ensures isinstance(d["a"], bool) == isinstance(d["b"], bool)` PROVES. CPython:
`{"a": True, "b": 1}` satisfies the precondition (`True == 1`) and violates the postcondition.

## Mechanism
Route #237's contract-side `hval_isinst_opaque h "bool"` is a function of the hval only; `True` and `1` are
both `HInt 1`, so equal hvals give equal answers. Python equality does NOT imply equal type.

## Repair direction
Fail-closed: refuse `isinstance(<hval>, bool)` (and `type(<hval>) is bool` etc.) in contracts, or make the
contract-side answer depend on something other than the `HInt` payload. A faithful fix needs a bool
constructor in the certified hval type (Phase2f certificate change) — out of scope for a quick repair.

## Probe census at 8260571f (`scratchpad/r245/probe-base.log`; CPython ground truth for each)
Shape: `f(d: Dict[str, PyVal])`, `requires d["a"] == d["b"]`, `ensures <test(d["a"])> == <test(d["b"])>`.
| contract-side test | base | CPython counterexample | verdict |
|---|---|---|---|
| `isinstance(_, bool)` | PROVED | `True` vs `1` | false claim -> REFUSED |
| `isinstance(_, int)` | PROVED | `1` vs `1.0` | false claim -> REFUSED |
| `isinstance(_, float)` | PROVED | `1.0` vs `1` | false claim -> REFUSED |
| `isinstance(_, set)` / `frozenset` | PROVED | `{1}` vs `frozenset({1})` | false claim -> REFUSED |
| `isinstance(_, bytes)` | PROVED | `b"a"` vs `bytearray(b"a")` | false claim -> REFUSED |
| `isinstance(_, S)`, `class S(str)` | PROVED | `S("x")` vs `"x"` | false claim -> REFUSED |
| `isinstance(_, type(None))` | PROVED | none (class not nameable -> refused, fail-closed) | REFUSED |
| `isinstance(_, dict/str/list/tuple/NoneType)` | PROVED | none: builtin `==` never crosses these types | kept (true claims) |
| `isinstance(_, object)` | PROVED | none (decided `true`) | kept |
| tuple form `isinstance(_, (bool, str))` | parse error | -- | fail-closed already |
| `type(_) is/== bool`, `_ is None` | parse error / "Undefined variable 'bool'" | -- | fail-closed already |
| `requires isinstance(d["a"], bool)` + body test | Timeout | -- | not provable (now refused) |
| program side `isinstance(<hval>, bool)` twice | FAIL | -- | sound: `(any bool)` fresh per evaluation |

## Repair landed (gen #36, 2026-10-16)
`expressions._handle_isinstance`, the route #237 hval arm (inline; mirror twin is a `\trusted` stub): in a SPEC
context, when some constructor arm is opaque AND some class named is outside the equality-closed set
{`dict`, `str`, `list`, `tuple`, `NoneType`, `object`}, the opaque arm is the application of the UNBOUND symbol
`pycsl_refused_contract_type_test_on_erased_hval` (no declaration): the contract is REFUSED at the WhyML
type-check (`unbound function or predicate symbol 'pycsl_refused_contract_type_test_on_erased_hval'`), the same
type-check-level answer route #240 gives a contract bool test on an int subject. Decided arms and the program
side (`(any bool)`) are unchanged. No raise (so no `\trusted`-raises / refusal-census / advice ledger row, per
lessons (c5)/(d5)), no new def, no declaration, no axiom; ledger 3.

## Witnesses (corpus, `gen36_r245`; CPython ground truth `scratchpad/r245/ground.log`, `witness.log`)
False claims PROVED at 8260571f, REFUSED (L3-tc unbound refusal symbol) after: 2300 (bool, `True`/`1`), 2301
(int, `1`/`1.0`), 2302 (float), 2303 (set/frozenset), 2304 (bytes/bytearray), 2305 (user `str` subclass).
Controls PASS at base and after: 2310 dict, 2311 str, 2312 tuple, 2313 list, 2314 program-side bool test.

## Gates (logs: `/tmp/claude-1000/.../scratchpad/r245/`)
- Witnesses: `witness.log` (11 files, both sides).
- Corpus byte-diff vs a fresh 8260571f worktree: root 1587 baseline / 1598 candidate, 0 MOVED, 0 GONE,
  0 APPEARED, 11 new sources; pyref 2198/2198, 0 MOVED, 0 GONE (`compare-root.log`, `compare-pyref.log`).
- Mirror: 53/53, 0 MOVED, 0 GONE (`compare-mirror.log`).
- Planes 61/61 (`planes.log`); sync rc=0 (916 verbatim); mirror-check rc=0.

## Residuals (NOT repaired here)
- **An int-erased `Any` subject's type test is a function of the int.** Route #239 made `isinstance(x, T)` on
  an `Any` subject `subtag (typeof_op x) T`, a logic function of the lowered value in BOTH program and spec
  context, and `1`/`1.0` (also `{1}`/`frozenset({1})`) are one int. `witnesses-r245/any_int_vs_float_in_contract.py`
  (`requires x == y`, `ensures isinstance(x, int) == isinstance(y, int)`) and
  `witnesses-r245/any_int_vs_float_program_side.py` (`if isinstance(x, int): if not isinstance(y, int): return 0`,
  `ensures \result == 1`) PROVE at this commit; CPython `f(1, 1.0)` breaks both (also `float`, `set` measured).
  `bool` on this path is already refused (#240). Needs its own route: the program-side fix (fresh per
  evaluation) costs #239's `requires isinstance(x, int)` -> body link (2212), so it is not a fail-closed one-liner.
- hval `==` is structural, while Python `==` crosses types for non-builtin classes (`UserString("x") == "x"`,
  custom `__eq__`): the DECIDED `HStr`/`HMap` arms rest on the builtin-values reading of `PyVal`. Recorded only.
