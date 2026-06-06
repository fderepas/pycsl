"""Test 0546 — or-pattern binding a payload across alternatives (A5c follow-on).

`case Some(n) | Wrapped(n):` binds the SAME capture `n` from either alternative
(Why3 requires an or-pattern's alternatives to bind identically). With `Some(5)`
the arm returns `n == 5`. Flips when the recursive pattern renderer emits
`| Some n | Wrapped n -> …` and Why3 accepts the shared binding.
"""
#@ datatype E = Other | Some(int) | Wrapped(int)
_ = 0  # anchor


#@ ensures \result == 5
#@ assigns \nothing
def get() -> int:
    e = Some(5)
    match e:
        case Some(n) | Wrapped(n):
            return n
        case Other():
            return 0
