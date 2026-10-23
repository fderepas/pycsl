# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL
"""1279 — (#49) ROUTE #98, THE SECOND RENAMING RULE. `whyml_ident` also LOWERCASES a
leading capital, so a parameter named `Buf` is emitted as `buf`.

This is the sibling of 1278 and it matters because it shows the defect is not about
reserved words specifically but about the NAME-SPACE MISMATCH: any rewriting rule inside
`whyml_ident` reopens route #96, so a repair that special-cased the reserved-word list
would have been another narrowing rather than a fix.

MEASURED AT a32ec69e: emitted `val scramble (buf: array int) (n: int) : int` with NO
`writes`, and PROVED `\result == 7`. CPython returns 0. Must FAIL after the repair.
"""


#@ requires n >= 0
#@ assigns Buf[0..n]
#@ \trusted reviewer: route98
def scramble(Buf: list, n: int) -> int:
    Buf[0] = 0
    return 0


#@ requires \length(arr) > 3
#@ requires arr[0] == 7
#@ ensures \result == 7
def driver(arr: list) -> int:
    scramble(arr, 1)
    return arr[0]
