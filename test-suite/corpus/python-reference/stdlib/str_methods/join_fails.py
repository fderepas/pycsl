"""sep.join([...]) — NEGATIVE (faithful-string-op.md §3.5).

Unsound to omit the separators from the length: n elements joined by sep add (n-1)*len(sep)
characters. Does NOT verify under --proof (str_concat_op's length law counts them).
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == len(a) + len(b)
def join_two_no_sep(a: str, b: str) -> int:
    return len(",".join([a, b]))


if __name__ == "__main__":
    pass
