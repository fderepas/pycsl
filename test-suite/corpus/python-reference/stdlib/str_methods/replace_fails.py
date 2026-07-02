"""str.replace(old, new) — NEGATIVE (faithful-string-op.md §3.1).

Unsound to claim length is preserved UNCONDITIONALLY: replace may grow/shrink the
string when len(old) != len(new). Does NOT verify under --proof (str_replace_op has
only the conditional equal-length law). Suite runs --no-proof (emission only).
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == len(s)
def replace_unconditional(s: str, a: str, b: str) -> int:
    return len(s.replace(a, b))


if __name__ == "__main__":
    pass
