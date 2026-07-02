"""str.strip()/lstrip()/rstrip() — str_strip_op (faithful-string-op.md §3.3).

Sound law: stripping only removes characters, so the result is no longer than the input.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result <= len(s)
def strip_shorter(s: str) -> int:
    return len(s.strip())


if __name__ == "__main__":
    pass
