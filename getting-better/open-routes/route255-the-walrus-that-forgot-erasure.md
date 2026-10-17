# OPEN ROUTE #255 — ERASURE IS LOST THROUGH A WALRUS BINDING AND THROUGH AN UNANNOTATED RETURN

**Status: REPAIRED (gen #36, 2026-10-17; opened 2026-10-16), Severity 1.** See "Repair" at the end. Red-team finding; driver-reproduced at HEAD fa283db6
(all four rc=0; CPython 7).

## Witnesses (`witnesses-r255/`)
- `p50_walrus_sub.py`: `if (v := x) is not None: return v - v` on `x: Any`, `ensures \result == 0` proves.
- `p45_walrus.py`: walrus value passed to `g(a: int, b: int)` — bypasses #252's refusal.
- `p51_unannot_sub.py`: `def h(z): return z`; `v = h(x); return v - v` proves `\result == 0`.
- `p47_untyped_local_from_call.py`: the unannotated-return value passed to int params.

## Mechanism
#249's erased-local fixpoint does not treat a `NamedExpr` target as bound from an erased value, and treats a
MISSING return annotation (and unannotated params lowered to `int`) as non-erased, so #251's uninterpreted
arithmetic and #252's flow refusal are bypassed.

## Repair direction
Walrus targets join the fixpoint; a function with no return annotation (and its unannotated params) counts as
erased (or the unannotated callee's return is erased at the call site). Census every binding form the fixpoint
might miss (for-targets, with-as, except-as, comprehension targets, tuple unpack, augassign, global/nonlocal).

## Repair (gen #36, 2026-10-17)
Why `h(z)` "lowered `z: int`": #249 DID erase the unannotated param inside `h`; the hole was at the CALL
SITE — the fixpoint erased a call result only for a module function declared `-> Any`/`object`, matched by
exact name, so `h(x)` was an ordinary `int`. Repaired inline in `functions.py::_reset_function_state`
(fixpoint) and `expressions.py::_handle_binop` (its walk copy reads the two new `_r249_scope` keys):
- BINDING FORMS: every statement with a value and `target`/`targets`/`tuple_targets` (adds `TupleUnpack`),
  every `NamedExpr` (walrus), every `match` capture (bound from the subject); a LAMBDA's params are bound
  from the arguments of the calls of the one name it is bound to (erased outright if it escapes / is
  rebound / is not bound to a name).
- CALL RESULTS (`any_ret`): a unit function or method whose return annotation is MISSING, `Any`, `object`
  or a TypeVar (registry or its own type params), resolved per call spelling: plain name, `self.m`,
  `obj.m` via the receiver's symbol type, `Class.m`, else by method short name. `__init__` excluded.
- `arg_prop`: `abs/max/min/sum/getattr/next/iter/sorted/reversed/list/tuple/set/dict/frozenset/
  enumerate/zip/map/filter/round/pow/divmod/vars/type`, `copy.*`/`operator.*`/`functools.*` and lambdas
  return an erased value iff handed one (or, a lambda, iff its body reads one); calling an erased name is
  erased. Builtins with a CPython-enforced result type (`len`, `str`, `int`, `isinstance`, ...) are exempt.
- `\result` of a function with no return annotation is erased in its own contract.
- #252 site filter: a top-level container LITERAL handed to a builtin slot is not an erased scalar (like
  the existing whole-container exemption) — the mirror's dict-as-`int` returns.
- Module3: the HAPPY-NI `__selfcomp` twin (returns literal 0) is now `-> int`.
Census of binding forms (probes, CPython 7 each): CLOSED walrus, tuple unpack, unannotated return,
TypeVar return, `obj.m()`/`self.m()` `-> Any`, lambda, `abs`/`max`/`getattr`, a direct `h(x) - h(x)`;
star-unpack (already FAIL at base, now refused too); ALREADY REFUSED before this route: `with ... as` (route `with`), `except ... as`
(#233), closure capture (lift refusal), walrus in a comprehension (#180), `global` write, `for` over an
`Any` iterable, `match` capture of an `Any` subject, augmented assign, unannotated default param.
Witnesses (PROVED at e6f26cde; CPython 7): 2550-2553, 2556-2562 REFUSED; 2554/2555 (arithmetic in a
branch) VERIFY-FAIL. Control 2566 PASS. Blast radius (each a FALSE or ill-typed claim): root GONE 1727 and
2214 (PASS -> REFUSED: `getattr(o, "a")` on `o: Any`, CPython 7) and 1859/1860/2205/2206 (FAIL ->
REFUSED); MOVED 1316/1691 (FAIL -> FAIL); pyref GONE 0059/0061/0141/0175/0205 (FAIL -> REFUSED) and the six
`stdlib/json/{dumps,load,loads}_call_{fails,proves}` drivers (PASS -> REFUSED: the stubs have no return
annotation and the drivers return a `str`/JSON value from `-> int`). Mirror 0 MOVED, 0 GONE.
Residual found, NOT this mechanism (reported for routing): `Optional[Any]` / `Optional[object]` /
`Any | None` / `Union[Any, None]` parameters lower to a union with ONLY the `None` arm (GT1 drops the
`Any` arm; `core_ir_semantic` only warns), so `if x is not None:` is dead in the model and
`def f(x: Optional[Any]) -> int: if x is not None: return 6 / return 5` PROVES `\result == 5`.
