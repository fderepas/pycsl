"""sep.join([...]) over a LITERAL string list — str_concat_op (faithful-string-op.md §3.5).

A literal list/tuple of strings joined by sep lowers to nested str_concat_op, EXACT: the
result length is the sum of element lengths plus (n-1) separator lengths.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == len(a) + len(b) + 1
def join_two(a: str, b: str) -> int:
    return len(",".join([a, b]))


#@ ensures \result == len(a) + len(b) + len(c) + 2
def join_three(a: str, b: str, c: str) -> int:
    return len("-".join([a, b, c]))


if __name__ == "__main__":
    pass
