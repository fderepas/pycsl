"""Test 0531 — guarded match pattern (A5c).

`case MSome(n) if n > 0` — a guard on a constructor pattern. With MSome(-5) the
guard is FALSE so control must fall to `case _` and return 0. Fails today: the
pattern parser drops the `if`-guard, so `case MSome(n)` matches unconditionally
and returns 1 — contradicting `ensures \\result == 0`. Flips when match lowering
threads the guard condition.
"""
#@ datatype Maybe = MNone | MSome(int)
_ = 0  # anchor


#@ ensures \result == 0
#@ assigns \nothing
def guarded() -> int:
    o = MSome(-5)
    match o:
        case MSome(n) if n > 0:
            return 1
        case _:
            return 0
