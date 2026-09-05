# OPEN ROUTE #42 — `<int> is True` / `<int> is False` proves a contract FALSE of the program

**Found 2026-09-05 by relaunch #46, at commit `21c9c335`. NOT CLOSED — scoped, measured,
and handed over rather than half-fixed at the end of a window.**

## The demonstration (default `hoare` model, no flags, verified by running Python)

```python
#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    x = 1
    if x is True:          # Python: `1 is True` is False -> f() returns 0
        return 7
    return 0
```
`[+] Verification SUCCESS! All contracts formally proven.`

Three more, all measured:

| program | model | Python |
|---|---|---|
| `x = 1; if x is True: return 7` | proves `\result == 7` | returns 0 |
| `x = 0; if x is False: return 7` | proves `\result == 7` | returns 0 |
| `x = 1; if x is not True: return 7` | proves `\result == 0` | returns 7 |
| `x = 1; if x == True: return 7` | proves `\result == 7` | returns 7 — **correct** |

The last row is the control: `==` is value equality and the model is right about it. The
defect is specifically `is`.

## The mechanism, and it is TWO conventions meeting

1. **Module 5 collapses `ast.Is` to `==`.** `_py_op_to_str` maps `Is` -> `"=="` and
   `IsNot` -> `"!="`, so by the time Module 6 sees the comparison the distinction between
   identity and equality is gone.
2. **Module 6 int-encodes `bool`.** `_handle_binop`'s documented "bool-as-int convention"
   rewrites a `Bool` literal operand of `==`/`!=` to `1`/`0`, so `x is True` emits `!x = 1`.

Each convention is defensible alone. Together they make `is` and `==` the same operator on
a bool literal, and Python says they are not: `is` is object identity, and a genuine `int`
is never the `True` singleton.

**This is the window's own general shape for the third time:** A PYTHON SINGLETON MODELLED
AS AN INTEGER LITERAL IS INDISTINGUISHABLE FROM THAT INTEGER INSIDE THE MODEL. Route #40
was `Ellipsis`; the recorded `None` residue is the second; this is the third.

## Why it was NOT closed here, stated precisely

**A blanket refusal breaks the mirror.** Census (`scratchpad/w46/census_isbool.py`, an AST
scan of `src/pycsl`, `src/self-annotate/src`, `src/pycsl_lib`, both corpora and `tests/`):

    56  `is False`      26  `is True`      12  `is not False`      = 94 sites

and TWELVE of them are in the self-annotation mirror
(`src/self-annotate/src/module6_whyml/functions.py`), all of the tri-state idiom
`if classify(e, pset, set()) is not False:` — a function that returns `True`/`False`/
something-else, where `is False` distinguishes the exact `False` from a merely falsy value.
Under the int-encoding convention those are internally consistent; refusing them would
break the mirror outright.

**The type-directed version is an UNDER-APPROXIMATION, i.e. the exact mistake routes #39
and #41 were about.** "Refuse when the operand is a Var whose symbol-table type is `int`"
closes the four rows above and leaves every Call-valued operand — including a call that
returns a plain int — unrefused. That is a blacklist keyed on a partial resolution, and
this window closed two routes that were exactly that.

**The whitelist version — "allow only when the operand is PROVABLY bool" — is the sound
shape and it is the one to build.** It needs the operand's type at the comparison site,
which Module 6 has for a Var (`_current_symbol_table`) but not for the mirror's
`classify(...)` Call. So the real prerequisite is:

## REOPENING CAPABILITY (build this, then the refusal is a whitelist)

**Give the IR a distinct `is` operator instead of collapsing it to `==` in Module 5**, and
give Module 6 a return-type for an intra-module call. Then:

* `<bool-typed> is True`  -> the current faithful `= 1`;
* `<anything else> is True/False` -> REFUSED (or an opaque bool), fail-closed by design;
* `is None` keeps its own existing handling, which is a separate and load-bearing path
  (see the `None` residue in the #46 handoff — do NOT fold the two together).

The `is`-vs-`==` split also unblocks the object-identity shapes, which today fail closed
only BY ACCIDENT on a Why3 type error: `a = [1]; b = [1]; if a is b:` and
`a = C(); b = C(); if a is b:` both die with "This expression has type array … @rho" /
"… PyCSL_Program.c @rho", not with a refusal and not with an unprovable goal. A
completeness fix could remove that accident at any time, and then those become live too.

## What is already done, so nobody redoes it

* The four exploits above are measured and reproducible; the drivers are in
  `scratchpad/w46/c8/` (`i_is_true.py`, `i_is_false.py`, `i_eq_true.py`, `i_is_int.py`,
  `i_is_notimpl.py`) and `scratchpad/w46/c9/` (`j_isnot_true.py`, `j_list_identity.py`,
  `j_obj_identity.py`).
* `x = 1000; y = 1000; if x is y:` PROVES and Python agrees (CPython folds the constant in
  the same code object), so it is NOT part of this route.
* `x is NotImplemented` fails closed on an unprovable goal, correctly.
* NO WITNESS IS COMMITTED TO THE CORPUS, deliberately: a `# pycsl-expected: FAIL` driver
  that currently PASSES would be an XPASS, and this campaign treats XPASS as a suite
  failure. The witnesses land WITH the fix.
