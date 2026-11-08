# FINDING (#49, gen #31) — the legacy `Generic[T]` spelling bypassed EVERY TY3 loud-fail

**STATUS: FOUND, MEASURED, ROOT-CAUSED TO ONE CONDITION, AND REPAIRED IN THE SAME SESSION**
(witnesses `1849`/`1850`, control `1851`). Not a demonstrated soundness route — what stops
one today is Why3's own typechecker, which is an accident rather than a design, and that
is the part worth reading.

## HOW IT WAS FOUND

By the same move as the day's other findings: take a sentence the documentation states as
a rule and write the program it describes. annotations.md §12.16 lists BOTH spellings in
its **Surface**:

> `class C[T]: ...`, `def f[T](): ...`, **`T = TypeVar("T", bound=B)` + `class
> C(Generic[T])`**

and its **Static plane** is *Interpreted*: whole-module monomorphization, with four
loud-fails — GT1 (`Any` never instantiates a TypeVar, "the consistency relation is
deliberately unsound"), GT2 (the TypeVar bound is an instantiation-time obligation), GT3
(ParamSpec/TypeVarTuple are schema-only), GT4 (polymorphic recursion).

## THE MEASUREMENT — ONE PROGRAM, TWO SPELLINGS OF THE SAME CONSTRUCT

| program | PEP 695 `class Box[T]` | legacy `class Box(Generic[T])` |
|---|---|---|
| `b: Box[int]` | emits `type box_int` (monomorphized) | emits `type box` — **NOT monomorphized**, `T` modelled as plain `int` |
| `b: Box[Any]` | **REFUSED** `PYCSL-TY3-GT1` | **Verification SUCCESS** |
| `T = TypeVar("T", bound=Base)`, `b: Box[int]` | (GT2) | **Verification SUCCESS** |

So all four loud-fails were silently inert for a spelling the documentation names, and the
TypeVar was modelled as `int`.

## ROOT CAUSE — A DEAD BRANCH, AND IT COULD NEVER HAVE RUN

`Module5_IREmitter.visit_ClassDef` attached the IR's `type_params` under

```python
**({"type_params": self._collect_type_params(node)}
   if getattr(node, "type_params", None) else {}),
```

`node.type_params` is the **PEP 695 attribute**. `_collect_type_params` has a whole second
half written for the legacy spelling — it walks the class bases for `Generic[...]`,
extracts the names with its own `_extract_generic_arg_names`, and resolves each against
`program_ir["typevar_registry"]`, which `_collect_typevar_registry` populates from
module-level `T = TypeVar("T"[, bound=B])` assigns to recover the bound. For a legacy
generic `node.type_params` is `[]`, so the guard was false and **the helper was never
called**. The monomorphization pass, where GT1–GT4 live, then early-returns because no
declaration carries `type_params`.

A dead branch with a docstring describing what it would have done, and no test to notice.

## THE FIX

Call the helper first and test ITS result:

```python
_tp695 = self._collect_type_params(node)
...
**({"type_params": _tp695} if _tp695 else {}),
```

`visit_ClassDef`'s mirror twin is `\trusted`, so the body owes no verbatim sync and no
re-proof.

MEASURED BEFORE/AFTER, with the "before" column taken from a worktree at HEAD:

| driver | before | after |
|---|---|---|
| `1849` legacy + `Box[Any]` | SUCCESS | **REFUSED** (GT1) |
| `1850` legacy + bound `Base`, instantiated `int` | SUCCESS | **REFUSED** (GT2) |
| `1851` legacy, never instantiated | SUCCESS | SUCCESS (the spelling stays legal — §12.16's "an un-instantiated generic emits NO specialized copy and is recorded Ignored/GT8") |

Byte-diff: 1336 -> 1337 reference `.mlw` (the one new control that emits), 0 MOVED / 0 GONE
/ 0 unexpected APPEARED; 2199 python-reference `.mlw` byte-identical.

## WHY IT IS NOT A DEMONSTRATED ROUTE, STATED HONESTLY

Three carriers were built and all three FAILED rather than proving something false, and in
every case the thing that stopped them was **Why3's typechecker, not PyCSL**: with `T`
modelled as `int`, a `Box[str]` holding `"abc"` emits `let b = { v = "abc" }` against
`type box = { mutable v: int }` and Why3 rejects it (`This expression has type string, but
is expected to have type int`); passing a `str` PARAMETER into the constructor fails the
same way at the boundary. So the int-modelling is caught wherever a concrete string meets
it.

That is a weak guarantee to be resting on. GT1's stated reason for existing is that the
consistency relation `Any` participates in "is deliberately unsound"; GT2's is that a
method verified against `T: Base` may use everything `Base` guarantees. Neither of those
obligations was being discharged for the legacy spelling, and the reason nothing had been
proved false is that nobody had written the program — which the census confirms: **ZERO
corpus files, ZERO `pycsl_lib` sources and ZERO mirror/live sources use the legacy
spelling** outside comments and string literals.

## A SECOND OBSERVATION, RECORDED BECAUSE IT IS ADJACENT AND UNFIXED

The generics feature has **no positive driver at all**. All three PEP 695 drivers in the
corpus (`1780`, `1781`, `1782`) are `# pycsl-expected: FAIL` witnesses. Monomorphization's
happy path is untested, and the probe here shows why it would be hard to write one: the
specialized type and method ARE emitted (`type box_int`, `let box_int__get`), but the
instantiation and the call still go through abstract ops (`val box_1`, `val b_get_0`), so
`Box(7).get() == 7` does not prove — in EITHER spelling. That is a pre-existing limitation
of the COLLECT/EMIT pass, equally present before this repair, and it is the capability the
next window would have to price to give generics a green driver.

Measured 2026-09-23.
