"""lv3 WITNESS (expected PASS): the truth test of a no-arg `<str>.split()`.

`s.split()` (whitespace runs) lowers to its own receiver-passing `array string`
`str_split_ws_op` (not `str_split_op s " "`, whose Python semantics differ), and
`if s.split()` to list non-emptiness `Array.length <a> <> 0`, instead of the
input-blind `s_split_0 ()` facade. The claim holds on both branches.
Control of 6824.
"""
# pycsl-expected: PASS


#@ ensures \result >= 0
def first_word_len(s: str) -> int:
    head = s.split()[0] if s.split() else s
    return len(head)
