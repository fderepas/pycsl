"""str.replace(old, new) — str_replace_op (faithful-string-op.md §3.1).

Sound length law: char-for-char replacement (len(old) == len(new)) preserves length.
Proves under --proof; the corpus runner uses --no-proof.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor


#@ requires len(a) == len(b)
#@ ensures \result == len(s)
def replace_eqlen(s: str, a: str, b: str) -> int:
    return len(s.replace(a, b))


if __name__ == "__main__":
    pass
