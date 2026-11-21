# OPEN ROUTE #612: a `Callable` parameter is assumed PURE

**Status: REPAIRED (refusal) on run #8, branch run8-u51 (executor u51), base 0057c8b94.** Found by lvX
(`scratchpad/run8/evidence/r612/callable_param_purity.py`). PRE-EXISTING: the lowering dates from the
typing-engagement ty3 delivery (§T.TY3.8, annotations.md §12.17) and is unrelated to run #8's models.

## Mechanism

§T.TY3.8 lowers `f: Callable[[A1, ..., An], R]` to a curried WhyML function-type parameter
`(f: a1 -> ... -> r)`, and the call `f(a1, ..., an)` to the application `(f a1 ... an)`. A WhyML arrow is
a MATHEMATICAL function. The model therefore assumed four things that no Python callable promises:

1. two applications to equal arguments are equal: `f(s) == f(s)` is decided True;
2. a body call equals the same application in a contract: `ensures \result == f(x)` over
   `return f(x)`, or `requires f(x) >= 0` then `return f(x)`;
3. a call changes nothing: an `assigns \nothing` claim, or a read of `len(xs)` after the call, keeps
   its old value although the callable appended to the caller's list;
4. a call returns, and returns normally.

A Python callable may keep state (`itertools.count`), mutate caller-visible state, raise, or not return.
Every spelling of an application reached the same pure value: `f.__call__(x)` (an abstract `val`, still
pure), a lambda wrapping `f`, a method parameter, and an annotated local alias `g: Callable[...] = f`.

## The rule (`PYCSL-R612-CALLABLE-ASSUMED-PURE`)

The check is in `_run_pipeline` (`src/pycsl/pycsl.py`). Its mirror twin is `\trusted`, so the change
needs no marker and moves no mirror emission. It is placed AFTER every other IR-semantic refusal, so
every existing witness keeps its own diagnostic.

A name whose `symbol_table` tag starts with `callable:` (a parameter, or an annotated local) may be
DECLARED and may not be REFERENCED. Two things are refused, anywhere in the function's IR (body,
nested lambdas, `requires` / `ensures` / `assigns`, assertions, invariants):
- a `Call` whose `func` is the name, or `<name>.<attr>` (an application);
- a `Var` of the name (the callable passed on, stored, aliased, compared or returned).

## Why this rule and not a fresh value per call

The measurement (grep + AST read + QUICK emissions at 0057c8b94):

| population | files writing a `Callable` parameter | of which emit | of which REFERENCE the parameter |
|---|---|---|---|
| `test-suite/corpus/pycsl-reference` (3275) | 15 | 5 (1853, 1854, 1878, 2586, 6641) | 1 (1878) |
| `test-suite/corpus/python-reference` (2185) | 0 | 0 | 0 |
| mirror `src/self-annotate/src` (53) | 0 | 0 | 0 |
| `src/pycsl_lib` | 0 (a comment only) | - | - |

(2586's `Optional[Callable]` lowers to the erased `Any` value, so it carries no `callable:` tag.)

The only emitting file that references a `Callable` parameter is control 1878:
`requires f(x) >= 0` / `return f(x)` / `ensures \result >= 0`. CPython falsifies that claim for a
stateful callable (probe p03, witness 10172), so the claim was never soundly provable.

A fresh `any` result per call would fix assumptions 1 and 2 only. To be sound it would also have to:
- havoc every caller-visible location at each call (assumption 3);
- refuse every `no_exception` and termination claim over a call (assumption 4).

That is large machinery, and the census shows it would serve no program in any of the three
populations. Refusing `Callable` parameters outright would be broader than needed: it would also take
1853, 1854 and 6641, whose claims never mention the callable and are sound. The chosen rule is the
narrowest one that removes all four assumptions without a model.

## Witnesses (corpus IDs 10170-10179)

| file | shape | base 0057c8b94 | HEAD |
|---|---|---|---|
| 10170 | `f(s) == f(s)` (lvX) | PROVED (hoare) | REFUSED |
| 10171 | `ensures \result == f(x)` / `return f(x)` | PROVED (hoare) | REFUSED |
| 10172 | `requires f(x) >= 0` / `return f(x)` | PROVED (hoare) | REFUSED |
| 10173 | `f(0)` then `len(xs)` | PROVED (hoare) | REFUSED |
| 10174 | `f.__call__(x) == f.__call__(x)` | Unknown (hardening) | REFUSED |
| 10175 | annotated alias `g: Callable[[int], int] = f` | Why3 type error (hardening) | REFUSED |
| 10176 | method parameter | PROVED (x3) | REFUSED |
| 10177 | CONTROL: declared, never referenced | PASS | PASS |
| 10178 | CONTROL: a verified function called by name | PASS | PASS |

The base and HEAD verdicts in all three memory models, with log paths, are in
`getting-better/run8-u51-report.md`.

Control 1878 is rewritten to `return 0`, keeping its subject (the declared-class DOMAIN of 1877).
Its old body is the shape of witness 10172.

## Residuals (not repaired here)

- **`Callable`-typed FIELDS** (`self.cb: Callable[[int], int]`, then `h.cb(x)`) carry no
  `callable:` symbol tag. See the report for their measured status (probes p09 / p18).
- `typing-engagement/ty3/conformance_callable/S5_pass.py` and `D1_no_blend.py` apply the callable
  (`ensures \result == f(n)`), so they are now refused. No gate runs them. Their claim is the false
  claim of witness 10171.
