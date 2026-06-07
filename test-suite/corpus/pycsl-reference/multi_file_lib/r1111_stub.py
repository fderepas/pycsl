"""multi_file_lib.r1111_stub — fixture for 1111-spec R5/R6/R7 (cross-module fidelity).

Exercises: a `str`-typed parameter (R5), a module-level integer constant (R6), and a
trailing parameter with a default (R7). `how` is intentionally NON-defaulted so a caller
omitting it triggers the R7 hard error.
"""
_ = 0  # anchor

SEEK_SET = 0


#@ requires how >= 0 and how <= 2
#@ ensures \result == how
#@ assigns \nothing
def clamp_seek(name: str, how: int, mode: int = 7) -> int:
    return how
