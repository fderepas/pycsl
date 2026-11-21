r"""Test 3752 -- gen #37 ch34 (expected PASS): the 2-argument `s.startswith(prefix, start)`. It lowered to the opaque receiver-DROPPED `s_startswith_2 prefix start` (the string tested was erased, `prefix` int-typed, result unconstrained); it now lowers to `str_startswith_from_op s prefix start`, true iff `prefix` occurs in `s` at index `start` (for 0 <= start). Honest claims must PROVE.
"""


#@ requires s == "xxab"
#@ ensures \result == 1
#@ assigns \nothing
def at_two(s: str) -> int:
    if s.startswith("ab", 2):
        return 1
    return 0


#@ requires s == "xxab"
#@ ensures \result == 0
#@ assigns \nothing
def past_end(s: str) -> int:
    if s.startswith("", 5):
        return 1
    return 0
