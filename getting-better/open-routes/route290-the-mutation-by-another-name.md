# OPEN ROUTE #290 — IN-PLACE MUTATION VIA operator.i*, DUNDERS, getattr, functools.partial, operator.methodcaller IS INVISIBLE
**Status: OPEN (gen #37, 2026-10-20), Severity 1.** Red-team round 8; driver-reproduced at 8d906404 (rc=0; CPython violates).
Witnesses `witnesses-r290/`. m001 `operator.imul(xs, 2)`, m005 `xs.__setitem__(0, 9)`, m006 `operator.methodcaller("reverse")(xs)`, m017 `getattr(xs,"reverse")()` / `xs.__delitem__(0)` / `functools.partial(list.reverse, xs)()` / `xs.__imul__(2)`: callee declares `assigns \nothing`, caller proves the list unchanged. #162 denylist lacks operator.i*; #280 guard does not match dunder names, getattr, partial or methodcaller. Repair: refuse (or model) every indirect/dunder/higher-order route to a mutator; census operator, functools, dunders of list/dict/set/bytearray.

## REPAIR (2026-10-20, worktree pycsl-rB off 7313506b)
Root cause (located on the IR of each probe): two independent carriers. (a) Module 5's `_py_expr_call`
catch-all erases a call whose CALLEE is a computed expression (`getattr(..)()`, `operator.methodcaller(..)(xs)`,
`functools.partial(..)()`, `(lambda: ..)()`, `(a if c else b)()`, `(t,)[0]()`, `(h := ..)()`) to
`{"type": "UnknownPyExpr"}` — the callee AND its arguments vanish; as an expression statement it emits
nothing, as a value `(any int)` (route #115) with no effect. (b) An explicit in-place dunder or an unbound
type method (`xs.__setitem__(0, 9)`, `list.__setitem__(xs, 0, 9)`, `xs.__imul__(2)`) and `operator.imul`
reach the generic abstract-op fallback, which takes no `writes`; #162's denylist lacked the other
`operator.i*` functions and #280's guard fires only on a COMPUTED receiver.

Probe table (`pycsl.py`, rc; 56-probe census under `scratchpad/rB/p290`, each `g(xs)` declared `assigns
\nothing`, caller claims the list unchanged; CPython mutates it in every probe; base = 7313506b):

| shape | base | after |
|---|---|---|
| `operator.imul(xs, 2)` (m001 / 3389) | PROVED | REFUSED (#162 denylist, extended) |
| `xs.__setitem__(0, 9)` (m005 / 3390), `xs.__delitem__(0)` (3393), `xs.__imul__(2)` (3395) | PROVED | REFUSED (2) |
| `operator.methodcaller('reverse')(xs)` (m006 / 3391), `methodcaller('append', 5)`, `('sort')`, non-literal name | PROVED | REFUSED (1)/(5) |
| `getattr(xs, 'reverse')()` (m017 / 3392), `getattr(xs, 'append')(5)`, `getattr(xs, '__setitem__')(0, 9)`, `getattr(xs, nm)()` | PROVED | REFUSED (1)/(5) |
| `functools.partial(list.reverse, xs)()` (m017 / 3394), `partial(xs.append, 5)()`, `partial(xs.reverse)()`, `partial(operator.setitem, xs)(0, 9)` (3398) | PROVED | REFUSED (1)/(4) |
| `list.__setitem__(xs, 0, 9)` (3396) | PROVED | REFUSED (2) |
| `(lambda: xs.reverse())()` (3397), `(xs.reverse if True else xs.sort)()`, `(xs.reverse,)[0]()`, `next(iter([xs.reverse]))()`, `(h := xs.reverse)()` | PROVED | REFUSED (1) |
| `h = xs.reverse; h()`, `h = xs.append; h(5)`, `list(map(xs.append, [5]))`, `for _ in map(xs.append, ..)`, `h = getattr(xs, 'reverse'); h()`, `h = operator.methodcaller('reverse'); h(xs)`, `xs.__iadd__([5])`, `list.__iadd__(xs, ..)`, `xs.__setitem__(slice(0, 1), [9])`, `operator.ior/isub(xs, ..)` | FAIL (ill-typed) | REFUSED |
| `list.reverse/append/sort/insert/pop/clear/extend/remove(xs, ..)` | FAIL (ill-typed / append-counter refusal) | REFUSED (3) |
| `heapq.heapify`, `bisect.insort`, `random.shuffle`, `operator.setitem/delitem/iadd/iconcat` | REFUSED (#162) | unchanged |
| `del xs[0:1]`, `type(xs).__setitem__(..)`, comprehension/generator calling `xs.reverse()` | REFUSED (other routes) | unchanged |
| `xs.__init__([7, 7])`, `xs.__class__.reverse(xs)`, `setattr(xs, 'x', 1)`, `h = lambda: xs.reverse(); h()` | FAIL (ill-typed) | unchanged FAIL (residual, fail-closed) |
| control 3399: a direct element store on the named receiver | PASS | PASS |

Rules:
- `pycsl.py::_run_pipeline` (the choke point: its mirror twin is `\trusted` and already raises, so no
  ledger moves; `_py_expr_call`'s stub is `\trusted` WITHOUT `#@ raises`, lesson d5), over the source AST,
  inline, new code `PYCSL-SEM-MUTATION-BY-ANOTHER-NAME`: (1) a call whose callee is neither a name nor a
  dotted attribute is refused, except the shapes Module 5 resolves to a real node (class-by-name factory
  `F(<lit|name|subscript>)(..)` of a one-line `return G[p]` function, the `getattr(self, <name>)(..)`
  dispatch, `type(self)(<pure args>)`) and an immediately-applied `lambda` whose body and arguments are
  PURE (names, constants, `+ - *`, comparisons, boolean ops, conditionals, tuples — 1313 stays emitted);
  (2) an explicit call of an in-place dunder (`__setitem__ __delitem__ __i<op>__ __setattr__ __delattr__`) on
  any receiver but `super()`; (3) an unbound mutating method of a collection type (`list dict set bytearray
  deque OrderedDict defaultdict Counter frozenset`); (4) a mutator (collection method name, in-place dunder,
  `operator.<setitem|delitem|i<op>>`) referenced as a VALUE rather than called; (5) `getattr(o, '<mutator>')`
  (`o` not `self`) and `operator.methodcaller(<name>)` naming a mutator, a dunder above, or a non-literal.
  Name-keyed and type-agnostic, so the dict/set/bytearray/deque spellings are covered by the same names.
- `expressions.py`, route #162's `_R162_ARG_MUTATORS`: + every other in-place `operator` function (`iand
  ifloordiv ilshift imod imul imatmul ior ipow irshift isub itruediv ixor`); fires only with a collection
  argument, as before.
Census (AST, the rule's own predicates, corpus root + pyref + mirror + `pycsl_lib`, before the rule): (1) 15
calls — `C()()` (pyref 0090, a callable instance), `depth[T](..)`/`ident[int](..)`/`fs[0](x)` (1783/1796/1314),
`Pick(..)(..)` (1315/1317: the class-by-name forms, exempt), `type(self)()` (0996; mirror `pure_ast` 5429,
exempt), the route #136-#138 `setattr` patches (1389/1391/1392/1396/1404) — every one already refused or a
FAIL except 1313 (pure lambda, exempt), 0090 (`C()()`, exempt: a no-argument same-file class whose
`__init__`/`__call__` neither store nor call) and 1314/1315/1317 (expected-FAIL route #115/#116 witnesses whose erased
callable call is now REFUSED — GONE, intended); (2) 4 / (3) 4 — all route #119/#120/#136/#138/#142 namespace
witnesses, already refused; (4) 4 — `chunks.append`-style aliases in the unannotated vendored
`pycsl_lib/json/decoder.py` (never lowered: not in any sweep); (5) 0 (the `getattr(node, field)` read in
mirror `pure_ast` names no mutator).
