# OPEN ROUTE #251 — ARITHMETIC ON `Any` IS INT ARITHMETIC; A USER `__sub__` BREAKS `x - x == 0`

**Status: REPAIRED (gen #36, 2026-10-16; opened the same day), Severity 1.** Residual of the #249 repair (same family as #227/#249);
driver-verified at HEAD c5c703ad: rc=0.

## Witness
`witnesses-r249/any_sub_self_is_zero.py`: `f(x: Any) -> Any: return x - x` with `ensures \result == 0` PROVES;
CPython can return 7 via a user `__sub__`.

## Mechanism
`Any`/erased values are ints, and `+ - * // %` on them lower to Why3 integer arithmetic with all its laws.

## Repair direction
Mirror #249: arithmetic with an erased operand lowers to uninterpreted `pycsl_py_add/sub/...` (no laws), keeping
integer arithmetic for builtin-typed operands. Measure the corpus blast radius first.

## Repair landed (gen #36, 2026-10-16) — route #249's design, for arithmetic and ordering

### Step 1: census (base aaf9b355, measured before any code)
A harness over `_handle_binop` and `_handle_unaryop_expr` logged every `+ - * / // % ** << >> & | ^ < <= > >=`
and unary `- + ~` lowering and classified its operands with route #249's OWN erased-operand walk (a synthetic
`==` over the same operands: did it answer `pycsl_py_eq`?): root 6058 sites, 1 erased (2375, a #249 witness);
pyref 5 erased in 4 files (0059, 0092, 0148, 0205: unannotated nested helpers / an `N` class); mirror 1039
sites, 16 erased (`peek(self, k=0)` in `pure_ast`/`Module2_Parser`, `_binop(self, min_prec)`, string
concatenations with an unannotated `pure_ast` unparser argument) (`census-base/`). `/`, `**` and the bitwise
operators were already law-free (`float_truediv_op`, `py_pow`, `bit_*` are uninterpreted), so they are not
touched. Counter-programs, each PROVED at aaf9b355 and FALSE in CPython (corpus 2440-2458, each file's
`__main__` is the ground truth): `x - x == 0` (2440, the route witness), commutativity (2441), `x + 0 = x` (2442),
`x * 0 = 0` (2443), `x % 1 = 0` (2444, CPython `0.5`), `<`-asymmetry in a program (2445) and a contract (2447),
`x <= x` (2446 program, 2458 contract: plain `nan`), `bool(-x) == bool(x)` (2448), `x >= 0 -> x // 2 >= 0`
(2449), through an augmented-assigned local (2450: `__iadd__` is its own method), a `List[Any]` element (2451),
`x + 1 > x` (2452, CPython `2.0 ** 53`), unannotated (2453), `object` (2454), TypeVar (2455) parameters, `~x`
truthiness (2456), a `-> Any` function's result (2457).

### Step 2: the rule
With an ERASED operand (route #249's population, unchanged), `+ - * // %` lower to the uninterpreted
`val function pycsl_py_add/_sub/_mul/_floordiv/_mod (a: 'a) (b: 'b) : 'c`, cast at every use to the operand
carrier (`real` if an operand is float-typed, else `int`), and `< <= > >=` to `pycsl_py_lt/_le/_gt/_ge
(a: 'a) (b: 'b) : bool`; unary `-`/`+`/`~` to `pycsl_py_neg/_pos/_invert (a: 'a) : 'a`. No axiom, no
definition, ledger 3; one symbol for contract and body (deterministic dunders, route #249's assumption).
Program-side `//`/`%` keep the int model's division-by-zero discipline (`pycsl_div`/`pycsl_mod` is still
evaluated on the once-bound operands) and the `no_exception` wrapper. Builtin-typed operands keep Why3
arithmetic (controls 2460-2463: `int` laws, `int` unary truthiness, `float` `<`-asymmetry, an `int` local
beside an `Any` parameter). A WHOLE `List[Any]`/`Set[Any]` container is erased for `==`/`in` (they compare
elements) but NOT for arithmetic (`xs + ys` is the builtin list's). A `str`-typed operand of `+`/`*`/`%` keeps
the string lowering (residual below).

Mechanism: route #249's erased-operand walk was MOVED (byte-identical, plus the container carve-out) from
the middle of `_handle_binop` to its head, where it also answers a probe op `r251_erased?` before anything is
lowered; the unary case asks that probe from `_expr_to_whyml`'s typed dispatch. No new def, no duplicate walk;
both edited methods (`_handle_binop`, `_expr_to_whyml`) have `\trusted` mirror twins. (A first cut placed the
unary case in `_handle_unaryop_expr`, whose mirror twin is a verbatim-checked converted body: `check-self-
annotate-sync` went RED, so it was moved.) Two live signatures were annotated so the mirror keeps its
proofs: `peek(self, k: int = ...)` in `frontend/pure_ast.py` and `frontend/Module2_Parser.py`, and
`_binop(self, min_prec: int)` in `pure_ast.py` (every live caller passes an int; the mirror copies carry the
same annotation, so the verified `peek` array-bound proof is unchanged — its emission is byte-identical to
base).

### Blast radius (logs: `/tmp/claude-1000/.../scratchpad/r251/`)
- Witnesses: `witness-base.log` (2440-2458 PROVED, 2460-2463 PASS), `witness-after.log` (2440-2458 FAIL,
  2460-2463 PASS); scratch probes `probe-base.log`/`probe-after.log`.
- Corpus byte-diff vs a fresh aaf9b355 worktree: root 1664 baseline / 1687 candidate, 1 MOVED (2375, a #249
  witness whose `x + 1` is now `pycsl_py_add`), 0 GONE, 0 APPEARED, 23 new sources (`compare-root.log`;
  `compare-root-declared.log` rc=0); pyref 2198/2198, 4 MOVED (0059, 0092, 0148, 0205), 0 GONE/APPEARED
  (`compare-pyref.log`, `compare-pyref-declared.log` rc=0). M1, every mover re-proved base and after
  (`m1.log`): 2375 FAIL -> FAIL (expected FAIL), pyref 0092 FAIL -> FAIL, 0148 PASS -> PASS, and 0059 / 0205
  PASS -> FAIL, now marked `# pycsl-expected: FAIL` with the reason in the docstring: TRUE claims
  (`add(1, 2) == 3`, `double(2) + 1 == 5`) whose nested helper has UNANNOTATED (`Any`) parameters, so the
  caller's int instance `pycsl_py_add 1 2` is no longer decided — the price of the rule, as #249's 1686.
- Mirror: 53/53, 1 MOVED (`frontend/pure_ast`: `_function_helper`'s string-plus-attribute and
  `require_parens`' `>`, both `ensures True` methods), 0 GONE; `why3 --type-only` rc=0 base and after
  (`compare-mirror.log`, `compare-mirror-declared.log` rc=0, `mirror-typeonly.log`). `Module2_Parser` is byte-identical to base after the `peek`
  annotation.
- Planes 61/61 (`planes.log`); `check-self-annotate-sync.sh` rc=0 (916 verbatim, `sync.log`); `self-annotate-mirror-check.sh`
  rc=0 (`mirror-check.log`). No edited live method with an un-`\trusted` mirror twin except the two
  annotated signatures, re-ported verbatim.
- NOT re-proved: the whole `pure_ast` mirror (its `--fun` path is broken at base: "unexpected 'variant'
  clause"); the two moved methods are `ensures True` and type-check clean. OWED.

## Residuals (NOT repaired here; each reproducer PROVES at aaf9b355 and after, `residual-*.log`)
- **An `Any` value passed to an `int` parameter or stored in an `int` field** is trusted to be an int:
  `g(a: int, b: int) ensures \result == a - b`, `f(x: Any) -> int: return g(x, x)` proves `\result == 0`
  (CPython: `__sub__ -> 7`); likewise `b = Box(x, x); return b.v - b.w` for `int` fields.
- **`no_exception` over an erased operation**: a user dunder may raise anything; `#@ no_exception \all` with
  `y = x - x` on `x: Any` PROVES (CPython: `__sub__` raises `ValueError`).
- **A `str`-typed operand** (`"a" + x`, `"ab" * x`, `"%s" % x`) keeps the string model; `x.__radd__`/`__rmul__`
  can return anything.
- **Builtins over an erased argument** (`abs(x)`, `max`, `min`, `round`) are not in route #249's walk, so
  `abs(x) - abs(x)` is not erased by the walk (here it happened not to prove).
