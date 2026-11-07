"""Test 1092 — ROUTE #52 negative witness: `is` BETWEEN TWO EQUAL STRINGS WAS DECIDED TRUE.

FALSE OF THE PROGRAM: `b` is built at RUN time and is a different object from the literal
`c`, so Python's `b is c` is False and `f()` returns 0.

Route #42 gave `is` its own IR operator, narrowed it back to `==` at `generate_json` and
whitelisted exactly one shape — an identity test against a `bool` LITERAL. Everything else
still means value equality. For an object whose `__eq__` is the DEFAULT one that is exactly
right, and it is why the enum, sentinel and class-object idioms in this tree are modelled
correctly. For a type with VALUE equality — `str`, `int`, `tuple`, ... — equality does not
imply identity. At the parent commit 22fdd54c `\\result == 7` PROVED.

THE REFUSAL IS A BLACKLIST AND THAT IS A MEASURED DEPARTURE from route #42's whitelist rule:
a whitelist would have to refuse the six non-singleton `is` sites in the whole tree, every
one of which the `==` lowering gets right, because nothing in the emitter can SHOW that a
name is identity-typed. Stated residue: an UNANNOTATED local holding a string is not refused.

THE SINGLETON FAMILY HAD TO BE EXEMPTED EXPLICITLY and `1087` is the control that holds it:
`x is None` runs through this same handler BEFORE routes #40/#44/#50 model it downstream, so
the first spelling of the refusal swallowed every `is None` on a string local and SEVEN of
the fifty-three mirror files stopped emitting (46 of 53) — against a census that predicted
zero. The census says where to look; only the measurement is the gate.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == 7
#@ assigns \nothing
def f() -> int:
    a: str = "a"
    b: str = a + "b"
    c: str = "ab"
    if b is c:
        return 7
    return 0


if __name__ == "__main__":
    assert f() == 0
