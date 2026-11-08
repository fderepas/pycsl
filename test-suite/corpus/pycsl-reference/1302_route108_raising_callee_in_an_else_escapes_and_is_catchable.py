"""Test 1302 — ROUTE #108 POSITIVE witness: the repair is FAITHFUL, not merely refusing.

After the repair the `else:` is lowered as a SIBLING of the try/except, so a callee raise
written there ESCAPES the wrapper exactly as Python propagates it — and a caller that
CATCHES it proves. Emitted (verbatim):

    let wrapper (k: int) : int
      raises { ValueError }
    =
      ...
      try  y := 1; try_else_ok'4 := True
      with ValueError -> y := 9
      end;
      if !try_else_ok'4 then begin
        let _ = (boom k) in ()
      end;
      !y

Note `raises { ValueError }` on `wrapper`: `_callee_raised_in` now visits `orelse`, so the
summary is honest. That half of the repair is NOT optional — once the else sits outside the
try, Why3's own exception typing rejects the file without it. (Measured separately: the
`finalbody` twin of this blindness is FAIL-CLOSED for exactly that reason.)

WHY A POSITIVE WITNESS IS REQUIRED. 1301 asserts that something must NOT prove. A repair
that simply refused every `try/else` containing a call would satisfy 1301 and destroy the
capability. Only this file can fail when that happens.
"""
_ = 0  # anchor
#@ raises ValueError when x0 < 0
#@ ensures \result >= 0
def boom(x0: int) -> int:
    if x0 < 0:
        raise ValueError("neg")
    return x0

#@ ensures \result == 1
#@ assigns \nothing
def wrapper(k: int) -> int:
    y = 0
    try:
        y = 1
    except ValueError:
        y = 9
    else:
        boom(k)
    return y

#@ ensures \result >= 1
#@ assigns \nothing
def catcher(k: int) -> int:
    try:
        return wrapper(k)
    except ValueError:
        return 42
