"""Static gate CA2 — cast honesty (no type check; "wrong" cast still PASSes).

Spec clause CA2 (cast-twoplane-spec.md §1, §4 — the honesty point): the
static "assertion" of `cast` is an UNCHECKED hint. PyCSL does NOT lower
`cast(t, v)` to a verification condition over `t`; there is no `requires`
clause over `t`, no narrowing predicate, no `v : t` proof goal. So a cast
that "claims" a type that does NOT match the value — `cast(str, 5)` — must
still PASS verification: cast is unchecked by definition (PEP 484), and a
shim/lowering that REJECTED a "wrong" cast would be blending the planes
(emitting a static obligation that S1/S2 grant no authority for and that
the runtime plane does not back).

This driver is the honesty check: `cast(str, 5)` (claiming str, value is
int) must still verify, with the identity postcondition discharging to 5.

Expected (from spec): PASS — cast does not verify the type; the identity
postcondition `\\result == 5` discharges regardless of the claimed type.
"""


#@ ensures \result == 5
def f() -> int:
    from pycsl_lib.typ import cast
    return cast(str, 5)


if __name__ == "__main__":
    assert f() == 5
    print("PASS")
