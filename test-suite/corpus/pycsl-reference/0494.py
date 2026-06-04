"""Test 0494 — strings: the `in` containment witness (Stage 4).

Strengthens 0474 (which only proved the 0/1 boundedness). As of strings-plan Stage 4,
`str_contains_op` carries the existential content witness
  result <-> (exists i. 0 <= i /\\ i + len(needle) <= len(haystack)
                        /\\ substring(haystack, i, len(needle)) = needle).
So a *known* occurrence of `needle` (here at index 0) lets the prover instantiate the
existential and conclude `needle in haystack` is true — the make-or-break content goal
(Gate B) discharged for membership, not just for the hand-written search loop (0471)."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(needle) <= \str_length(haystack)
#@ requires \str_sub(haystack, 0, \str_length(needle)) == needle
#@ ensures \result == 1
def has_prefix_occurrence(haystack: str, needle: str) -> int:
    if needle in haystack:
        return 1
    return 0
