"""Test 0471 — DEMAND-DRIVER for strings-plan.md: substring / pattern search.

This is the concrete use case that justifies promoting runtime `str` to Why3 `string`
(see `strings-plan.md`). `find_pattern` scans `haystack` for the first occurrence of
`needle` and returns its index, or -1. Its specification is exactly the content-level
string reasoning the feature must enable:

  - body: `len(s)`, slicing `s[i:j]`, and content equality `==` on runtime `str` params;
  - spec: `\str_length` / `\str_sub` and string `==` relating the result to the match.

STATUS — currently **UNSUPPORTED** (hence `# pycsl-expected: FAIL`). Runtime `str` is
modeled as an opaque int hash (`τ(str) = int`), so `len`, slicing, and `==` on a `str`
parameter carry no real string semantics and the postcondition cannot be discharged. This
file is the **target** the strings feature must make verifiable, and the **Stage-0
content-reasoning probe**: the "found ⇒ the substring at that index equals `needle`"
postcondition is substring-equality, the make-or-break SMT goal. It flips to expected-PASS
when (and only when) the feature lands and that goal proves.
"""
# pycsl-expected: FAIL
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
