# OPEN ROUTE #52 — `is` BETWEEN TWO VALUE-TYPED OPERANDS IS DECIDED BY VALUE EQUALITY
# (found 2026-09-08 by relaunch #49 at `5d74b620`; route #42's residue, one type wider)

## The demonstration (`scratchpad/w49/probeinv/s1.py`, `[+] Verification SUCCESS`)

```python
#@ ensures \result == 7          # <-- FALSE OF THE PROGRAM: Python returns 0
#@ assigns \nothing
def f() -> int:
    a: str = "a"
    b: str = a + "b"             # built at RUN time -> a fresh object
    c: str = "ab"                # a compile-time constant
    if b is c:                   # Python: False.  Model: `str_eq_op b c` -> True
        return 7
    return 0
```

Route #42 gave `is` its own IR operator and narrowed it back to `==`/`!=` at
`generate_json`, carrying the additive `py_is` marker, and whitelisted exactly ONE shape in
`_expr_to_whyml`: an identity test against a `bool` LITERAL. Everything else still lowers to
`==`. For an object whose `__eq__` is the DEFAULT (identity) that is exactly right — and that
is why the idiom survives everywhere it is used. For a type with VALUE equality — `str`,
`int`, `float`, `bytes`, `tuple`, `list`, `dict`, `set`, `frozenset` — equality does not imply
identity, and the model decides the test as equality.

## Controls, all measured at the same commit

| probe | shape | model | Python |
|---|---|---|---|
| `s1.py` | `<runtime-concat str> is <literal str>`, equal values | **PROVES** | 0 (False) |
| `s2.py` | `[1,2] is [1,2]` | fails closed | 0 (False) |
| `s3.py` | `x = 1000; y = 500 + 500; x is y` | proves | **7 (True)** — CPython folds the constant and shares it, so the model AGREES here; it is not a witness |
| `s4.py` | `a is a` | proves | 0 (True) — the control that any repair must not break |

`s3` is worth keeping because it is the trap: an `int` identity test can be True or False
depending on the interpreter's caching, and a repair that answers it either way is guessing.

## CENSUS — the population is tiny and it is NOT the value-typed one (AST scan, this tree)

`is` / `is not` comparisons where NEITHER side is a `None`/bool/`Ellipsis` literal:

    mirror   3    live  27    src/pycsl_lib  1    pycsl-reference  2    python-reference  3

and every one of them is an IDENTITY-typed operand, i.e. exactly the case the current
lowering gets right:

    pure_ast.py:5007          `operator_precedence is not _Precedence.FACTOR`   (enum member)
    Module5_IREmitter.py:3291 `stmt.value.value is Ellipsis`                    (route #40)
    statements.py:1309        `stmt.origin is not _ABSENT`                      (sentinel object)
    python-reference/0040     `x is NotImplemented`
    python-reference/0041     `x is Ellipsis`
    python-reference/0082     `type(C) is Meta`                                 (class object)

**So a repair that refuses only VALUE-TYPED operands is byte-inert by measurement, and a
blanket refusal of non-singleton `is` is NOT** — it would break the enum and sentinel idioms
the mirror itself uses, which are the cases the `==` lowering models correctly.

## REOPENING CAPABILITY — and route #42's own lesson decides its shape

Route #42 chose a WHITELIST over a type-directed refusal because "refuse when the operand is
an int-typed Var" is an under-approximation that leaves every Call-valued and unannotated
operand unrefused. The same argument applies here, so the rule must be: **admit `is` → `==`
only where the emitter can SHOW that equality implies identity** — both operands a
`None`/`Ellipsis`/`NotImplemented` singleton, a name the symbol table types as a class
instance or an enum member, a module-level sentinel binding, or syntactically the SAME
variable (`x is x`) — and REFUSE otherwise, naming what it could not show.

The honest cost of that inversion must be measured before it lands: it is the six sites
above, and if any of them cannot be SHOWN identity-typed the refusal breaks a mirror file and
owes either a widening of the whitelist or a `# noqa`-style annotation. That measurement is
the first step of the build, not an afterthought.
