"""Test 1015 — ROUTE #31 negative witness: the truthiness of a list local was
`true` for EVERY list, including the empty one.

FALSE OF THE PROGRAM: `[]` is FALSY in Python, so the guard is not taken and
Python returns 2.

At the parent commit c4233fed this printed `[+] Verification SUCCESS!` from the
emission `if true then begin 1 end else begin 2 end`. `_to_bool` answered `true`
for any name in `_array_locals`, with the comment "Array locals can't be compared
with <> 0; emit true (always allocated)" — ALLOCATION IS NOT TRUTHINESS.

`Array.length <> 0` was not the repair on its own: an empty list literal lowers
to the PLACEHOLDER `Array.make 1024 0`, so the Why3 length of the one case that
matters is 1024. The faithful length is the one `len()` already uses, and it is
now used here too — this file's true twin (`\result == 2`) PROVES, and so does
the non-empty case `a = [7]`.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    a = []
    if a:
        return 1
    return 2
