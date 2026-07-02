"""str.split(sep)[i] — NEGATIVE (faithful-string-op.md §3.4).

Unsound to claim a split piece equals the whole string's length: the separators are
removed. Does NOT verify under --proof (str_split_elem_op claims only <= len(s)).
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == len(s)
def split_head_full_length(s: str, sep: str) -> int:
    return len(s.split(sep)[0])


if __name__ == "__main__":
    pass
