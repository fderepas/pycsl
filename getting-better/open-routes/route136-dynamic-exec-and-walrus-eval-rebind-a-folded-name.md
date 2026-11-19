# ROUTE #136 — a DYNAMIC `exec`, and an `eval` that binds through a walrus, rebind a name whose value the model has already folded

**Status: CLOSED AND FULLY GATED (gen #26).** Severity 1. Both directions measured: every
shape below PROVED a postcondition that CPython contradicts, at HEAD `ddab1309`.

## The deferral that was the fence

`src/pycsl/frontend/exec_splice.py`'s module docstring says:

> A DYNAMIC `exec` (non-constant argument) is left untouched here; it is handled
> conservatively downstream (scope havoc + frame taint, P5a/P5a').

and, of the sibling parser-family builtins:

> (`eval`/`compile`/`ast.parse` return values and do not inject names — they don't havoc
> scope; their unknown *result* is handled separately.)

Both named handlers were LOCATED (generator: *deferral-audit* — locate the named guard and
quote its actual matching rule):

* `module6_whyml/functions.py` `_scope_dyn_exec` / `_has_dynamic_exec` — the ONLY thing it
  does is **withhold the `\in_scope` decided-FALSE direction**. It is computed per FUNCTION,
  from `func["body"]`, so it never sees a module-scope `exec` at all.
* the typed/store memory model's `exec_havoc … writes {int_mem}` — a HEAP frame taint, and
  only under `--memory-model typed`/`store`. It says nothing about a folded constant, an
  import binding, a def name or a builtin.

Neither handler touches a **value**. And the eval claim is false as of Python 3.8: `eval`
evaluates an *expression*, and `(N := 5)` is an expression that **binds**.

## Measured (each PROVES; CPython contradicts)

| witness | shape | model | CPython |
|---|---|---|---|
| 1382 | `N = 3; exec("N" + " = 5")` at module scope | `f() == 3` | 5 |
| — | `N = 3; S = "N = 5"; exec(S)` | `f() == 3` | 5 |
| 1383 | `exec("le" + "n = sum")` then `len([5])` | `== 1` | 5 |
| 1384 | `exec("in" + "c = dec")` over an imported `inc` | `inc(3) == 4` | 2 |
| 1385 | `exec("in" + "c = lambda y: y - 1")` over a module `def inc` | `inc(3) == 4` | 2 |
| 1386 | `N = 3; eval("(N := 5)")` at module scope | `f() == 3` | 5 |
| 1387 | in a function: `exec(code, globals()); return N` | `\result == 3` | 5 |
| 1388 | in a function: `eval("(N := 5)", globals()); return N` | `\result == 3` | 5 |
| 1394 | `ex = exec; ex("N" + " = 5")` | `f() == 3` | 5 |
| 1395 | `import builtins; builtins.setattr(plainlib, "inc", plainlib.dec)` | `inc(3) == 4` | 2 |
| 1396 | `getattr(builtins, "set" + "attr")(plainlib, "inc", plainlib.dec)` | `inc(3) == 4` | 2 |
| 1398 | `eval("globals().update({'N': 5})")` — constant text, no walrus | `f() == 3` | 5 |
| 1399 | `eval("exec('N = 5')")` | `f() == 3` | 5 |
| 1400 | `operator.setitem(globals(), "N", 5)` | `f() == 3` | 5 |
| 1401 | `dict.update(globals(), N=5)` | `f() == 3` | 5 |

1394-1401 are **second-order carriers of this route's own successive drafts** — every one was
found by carrier-rerun *before* a verdict was read (the battery was stopped twice, at 3 and
2 minutes in), and every one widened the repair. NINE drafts.

## Why the constant-`exec` fences did not cover it

Route #131/#132 added a token rule for `exec`: it requires `isinstance(call.args[0],
ast.Constant)`. Route #118 refuses a constant `exec` naming a function or class. A
non-constant argument steps outside all of them, and `_ExecSplicer` deliberately leaves it
alone.

## The repair (one region in `Module3_Weaver.process`)

Scoped to **where the binding actually reaches the module namespace**. A bare
`exec`/`eval` assigns into the LOCALS mapping; that mapping *is* the module globals at
module and class-body scope and is a discarded snapshot inside a function. So:

* refuse an `exec` whose first argument is not a string `Constant`, and an `eval` whose
  first argument is not a string `Constant` or whose constant text contains `:=`, **when**
  the call sits in the module-executed region (module or class body, including lambda
  bodies, def defaults/annotations/decorators and class headers — see route #137) **or**
  it is given an explicit mapping argument (`len(args) > 1` or any keyword) anywhere;
* refuse a namespace-reaching builtin (`exec eval setattr delattr globals vars locals
  getattr`) READ AS A VALUE, reached as an ATTRIBUTE (`builtins.setattr`), or reached by a
  computed `getattr` USED AS A CALLEE. *Every* namespace guard in the tree — #118's
  namespace-dict rule, #119's setattr/delattr rule, #127's computed getattr, and this
  route's own first cut — keys on the builtin's SPELLING, and one alias defeats them all.
  `__import__` is deliberately NOT in the list: no recognizer keys on it, and
  python-reference 0127 reads it as a value and PASSES;
* treat a CONSTANT `eval` text that NAMES a namespace builtin as binding too (`eval(
  "globals().update({'N': 5})")` has no walrus). python-reference 0109/0217 are
  `eval("2 + 3")` — no identifiers — and keep their verdicts;
* refuse a NO-ARGUMENT `globals()` / `vars()` / `locals()` call anywhere except bound to a
  plain name (route #116's `_g = globals()` idiom, itself fenced by #134) or read through a
  subscript. That dict IS the module namespace, and #118 only ever keyed on a subscript
  STORE *through* it — never on it leaving. `vars(self)` HAS an argument (an ordinary
  object's `__dict__`) and is untouched.

## Census (the reason the scoping is not arbitrary)

| tree | dynamic `exec` | constant `exec` | `eval` | ns-builtin as a value | `.<ns-builtin>` | `getattr(...)(...)`|
|---|---|---|---|---|---|---|
| pycsl-reference | 3 | 4 | 0 | 0 | 0 | 6 (all `_N(cls)(...)`) |
| python-reference | 0 | 0 | 2 | 1 (`__import__`) | 0 | 1 |
| 53 mirrors | 0 | 0 | 0 | 0 | 0 | 164 (all `_N(cls)(...)`) |
| `src/pycsl_lib` | 0 | 0 | 0 | 0 | 0 | 0 |
| `src/pycsl` | 0 | 0 | 1 | 0 | 0 | 169 (all `_N(cls)(...)`) |

All three pycsl-reference dynamic execs (0638, 0639, 0644) are **bare `exec(code)` inside a
function or method**, and both python-reference evals (0109, 0217) are constant and
walrus-free, so the six live sites are untouched and 0638/0639/0644 keep demonstrating the
`\in_scope` havoc and the frame taint. `src/pycsl/module6_whyml/auto_trust.py:188`'s
`eval(test_expr)` is a bare in-function dynamic eval — allowed — and its mirror is
`\trusted`, so it carries no eval at all.

## Lesson

> **A DEFERRAL THAT NAMES TWO HANDLERS CAN BE HONEST ABOUT BOTH AND STILL BE A HOLE.** The
> `exec` deferral named `\in_scope` havoc and frame taint, and BOTH exist and BOTH work.
> What it never said is that neither of them is about a *value*. Locate the named guard,
> quote its matching rule, and then ask *which of the three planes it actually covers*.
