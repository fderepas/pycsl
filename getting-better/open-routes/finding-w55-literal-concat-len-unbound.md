# FINDING (COMPLETENESS, NOT A ROUTE) — `len()` OF A LITERAL-LITERAL STRING CONCAT EMITS
# AN UNBOUND `concat` SYMBOL
# (found 2026-09-11 by relaunch #55, while probing string identity as a dict key)

## THE TRIGGER IS NARROW AND IT TOOK FOUR PROBES TO PIN

    s = "a" + "b"
    return len(s)          # Why3: "unbound function or predicate symbol 'concat'"

**BOTH halves are required.** Each on its own is fine, measured:

| shape | verdict |
|-------|---------|
| `s = "a" + "b"; return s` (`ensures \result == "ab"`)        | **PROVES** |
| `return "a" + "b"`                                           | **PROVES** |
| `def f(a: str, b: str): s = a + b; return len(s)`            | **PROVES** |
| `def f(a: str, b: str): s = a + b; return s`                 | **PROVES** |
| **`s = "a" + "b"; return len(s)`**                           | **UNBOUND `concat`** |

So it is specifically a LITERAL-operand concat bound to a local and then measured with
`len()`. The driver the docs cite for concat content (`0765`) uses string PARAMETERS and
never takes `len` of the result, which is why the corpus never hit this.

## WHY IT IS NOT A ROUTE, AND WHY IT IS STILL WORTH FIXING

It FAILS CLOSED — an unbound symbol is a Why3 type error, so BOTH directions fail and no
false claim can prove through it. It is a COMPLETENESS bug: a valid Python program is
rejected. The quality complaint is that it is rejected with an INTERNAL Why3 error rather
than a PyCSL diagnostic, which reads like a crash rather than a boundary.

## WHERE TO LOOK

This is the same fold machinery route #60 lived in. `types.py::_track_collection_metadata`
registers a size for `vt == "String"` (a bare literal), but a concat's `vt` is a BinOp, so
no size is registered; `_handle_len_call` then falls through to the string-length bridge,
which in a BODY context emits the `concat` term without the declaration that a spec context
would have. Compare with the `str_length_op` abstract-`val` path immediately below it in
`module6_whyml/expressions.py::_handle_len_call` — that path is the one that works for
parameters.

**A candidate fix that stays in the safe direction:** constant-fold `len()` of a concat
whose operands are both string LITERALS to the integer sum of their lengths — Python's
answer exactly, no symbol needed. Route #60's caution applies: fold only where the operands
really are literals, and refuse rather than guess otherwise.
