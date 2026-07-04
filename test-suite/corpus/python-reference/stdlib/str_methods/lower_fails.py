"""str.lower()/upper() — NEGATIVE (faithful-string-op.md §3.2).

Unsound to claim case folding preserves length: "ß".upper() == "SS" (1 -> 2), "İ".lower()
grows. Does NOT verify under --proof (str_lower_op/str_upper_op claim only the non-emptiness bound + idempotence).
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == len(s)
def lower_preserves_length(s: str) -> int:
    return len(s.lower())


if __name__ == "__main__":
    pass
