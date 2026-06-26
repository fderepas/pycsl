"""Static gate CA1 — cast identity (postcondition discharges).

Spec clause CA1 (cast-twoplane-spec.md §1, §4): `cast` carries NO static
obligation — it is Shimmed on the static plane (the unchecked assertion is
recorded as a hint, NOT lowered to a `requires`/`ensures` VC over `t`). The
only thing the static plane can observe about `cast(int, 5)` is the
identity postcondition inherited from the runtime shim, and that identity
trivially discharges for the literal 5.

This driver is the degenerate positive case: the postcondition
`ensures \\result == 5` must discharge because `cast(int, 5)` returns 5
unchanged.

Expected (from spec): PASS — identity postcondition discharges.
"""


#@ ensures \result == 5
def f() -> int:
    from pycsl_lib.typ import cast
    return cast(int, 5)


if __name__ == "__main__":
    assert f() == 5
    print("PASS")
