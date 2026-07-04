"""str.lower()/upper() — str_lower_op/str_upper_op (cleared-string RESIDUALS item 1).

Sound law: case folding never maps a non-empty string to empty (non-emptiness bound).
NB it is NOT length-preserving in Unicode ("ß".upper() == "SS"), so only this bound holds.
"""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor


#@ requires len(s) >= 1
#@ ensures \result >= 1
def lower_nonempty(s: str) -> int:
    return len(s.lower())


if __name__ == "__main__":
    pass
