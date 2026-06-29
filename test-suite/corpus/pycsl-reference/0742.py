"""Test 0742 — WhyML string literal with embedded newline.

Why3 string literals (`"..."`) reject raw control bytes (LF, CR, TAB, ...) with
"illegal character in string" (see why3 `src/util/lexlib.mll`, rule `string`).
A Python `"\n"` therefore lowered to a WhyML literal containing a raw newline,
which made any body-faithful annotation of code that builds strings via
`code += ";\n"` (the 24 `_handle_*` WhyML emitters in
`src/self-annotate/src/module6_whyml/statements.py`) unprovable. PyCSL now
escapes `\n` (and `\r`, `\t`, `\b`, `\\`, `\"`, and other non-printable bytes) to
Why3-accepted backslash escapes / hex-byte escapes, so a Python `";\n"` lowers to
the Why3 literal `";\n"` (backslash-n) and the body type-checks and proves.

The postconditions are intentionally trivial (`ensures True`): Why3's SMT
back-ends do not axiomatize the *contents* of string literals, so
`String.length ";\n" = 2` is Unknown to Z3/Alt-Ergo — a separate Why3 limitation,
not this gap. The witness here proves the literal is well-formed WhyML that
type-checks as `string` and that a body building a string with `+= ";\n"`
compiles and discharges its trivial contract — exactly what the 24 `_handle_*`
emitters need to go body-faithful.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures True
#@ assigns \nothing
def return_newline_literal() -> str:
    return ";\n"


#@ ensures True
#@ assigns \nothing
def build_newline_via_concat(prefix: str) -> str:
    return prefix + ";\n"


#@ ensures True
#@ assigns \nothing
def concat_around_newline(a: str, b: str) -> str:
    return a + ";\n" + b


if __name__ == "__main__":
    assert return_newline_literal() == ";\n"
    assert build_newline_via_concat("a") == "a;\n"
    assert concat_around_newline("a", "b") == "a;\nb"
    print("PASS")
