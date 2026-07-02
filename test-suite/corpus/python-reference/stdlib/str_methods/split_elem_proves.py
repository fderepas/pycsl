"""str.split(sep)[i] / rsplit(sep,k)[i] — str_split_elem_op (faithful-string-op.md §3.4).

Sound law: every split piece is a substring of the receiver (separators removed), so no
piece is longer than the input. Covers the emitter idiom func.rsplit(".",1)[0].
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result <= len(s)
def split_head(s: str, sep: str) -> int:
    return len(s.split(sep)[0])


#@ ensures \result <= len(s)
def rsplit_head(s: str) -> int:
    return len(s.rsplit(".", 1)[0])


if __name__ == "__main__":
    pass
