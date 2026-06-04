"""Test 0471 — DEMAND-DRIVER for strings-plan.md: substring / pattern search.

This is the concrete use case that justifies promoting runtime `str` to Why3 `string`
(see `strings-plan.md`). `find_pattern` scans `haystack` for the first occurrence of
`needle` and returns its index, or -1. Its specification is exactly the content-level
string reasoning the feature must enable:

  - body: `len(s)`, slicing `s[i:j]`, and content equality `==` on runtime `str` params;
  - spec: `\str_length` / `\str_sub` and string `==` relating the result to the match.

STATUS — **PROVES** as of strings-plan Stage 2 (runtime `str` is now Why3`string`). `len`,
slicing, and content `==` on `str` params carry real string semantics: the loop body's
`haystack[i:i+m] == needle` lowers to `str_eq_op (str_sub_op haystack i m) needle`, and on a
match the postcondition `\str_sub(haystack, r, r+\str_length(needle)) == needle` discharges by
rewriting through the `str_sub_op`/`str_eq_op` bridges to `String.substring haystack i m =
needle`. This was the make-or-break content-reasoning probe (Gate B) — it being provable is
what justified the feature.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(needle) >= 1
#@ requires \str_length(needle) <= \str_length(haystack)
#@ ensures \result == -1 or (0 <= \result and \result + \str_length(needle) <= \str_length(haystack))
#@ ensures \result >= 0 ==> \str_sub(haystack, \result, \result + \str_length(needle)) == needle
#@ assigns \nothing
def find_pattern(haystack: str, needle: str) -> int:
    n = len(haystack)
    m = len(needle)
    i = 0
    #@ loop invariant 0 <= i and i <= n - m + 1
    #@ loop variant n - i
    while i + m <= n:
        if haystack[i:i + m] == needle:
            return i
        i = i + 1
    return -1
