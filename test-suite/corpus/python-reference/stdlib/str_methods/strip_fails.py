"""str.strip()/lstrip()/rstrip() — NEGATIVE (faithful-string-op.md §3.3).

Unsound to claim strip preserves length: leading/trailing whitespace is removed. Does NOT
verify under --proof (str_strip_op claims only len(result) <= len(s)).
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == len(s)
def strip_preserves_length(s: str) -> int:
    return len(s.strip())


if __name__ == "__main__":
    pass
