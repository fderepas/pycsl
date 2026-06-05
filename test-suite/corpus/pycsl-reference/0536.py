"""Test 0536 — nested constructor patterns (A5c, `case Wrap(A(n)):`).

A constructor pattern may nest another constructor pattern: `case Wrap(A(n)):`
destructures two levels and binds `n` from the inner payload. Fails today: the
lowering renders only the top constructor's direct captures and collapses any
nested constructor sub-pattern to `_`, so the inner binding `n` is lost (and
`n` becomes an unbound `val constant`). With `Wrap(A(7))` and `ensures \\result
== 7`, a correct nested pattern binds `n = 7`; a collapsed one cannot. Flips
when the capture sub-patterns are rendered recursively (`| Wrap (A n) -> …`).
"""
#@ datatype Inner = A(int) | B
#@ datatype Outer = Wrap(Inner) | Nil
_ = 0  # anchor


#@ ensures \result == 7
#@ assigns \nothing
def unwrap() -> int:
    o = Wrap(A(7))
    match o:
        case Wrap(A(n)):
            return n
        case _:
            return 0
