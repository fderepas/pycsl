"""str.lower()/upper() — NEGATIVE (faithful-string-op.md §3.2).

Unsound to claim case folding preserves length: "ß".upper() == "SS" (1 -> 2), "İ".lower()
grows. Does NOT verify under --proof (str_case_op claims only the non-emptiness bound).
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == len(s)
def lower_preserves_length(s: str) -> int:
    return len(s.lower())


if __name__ == "__main__":
    pass
