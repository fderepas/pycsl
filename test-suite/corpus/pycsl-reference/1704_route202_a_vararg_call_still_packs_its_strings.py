r"""Test 1704 - ROUTE #202 control (gen #30): a VARARG formal PACKS every remaining actual into one sequence, so those actuals are not a parameter mismatch and must not be refused. Corpus 0931 (`def member_of(x: str, *vals: str)`, called `member_of("+", "+", "-")`) is the live instance, and the first draft of the #202 predicate flagged it - it mapped actual[1] onto formal[1] = `vals`, found no annotation for a vararg and found `vals` read by the contract. The census caught that before the gate was built; this witness keeps it caught.
"""
# pycsl-expected: PASS

_ = 0  # anchor


#@ requires True
#@ ensures x in vals ==> \result == 1
#@ ensures not (x in vals) ==> \result == 0
def member_of(x: str, *vals: str) -> bool:
    return x in vals


#@ requires True
#@ ensures \result == 1
def probe() -> bool:
    return member_of("+", "+", "-")
