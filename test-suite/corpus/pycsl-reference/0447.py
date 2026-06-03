"""0447 — string predicate methods (str.islower / startswith / endswith) are
modeled as uninterpreted 0/1-valued ops, so a function returning the predicate
proves `\result == 0 or \result == 1`. Body-verified, 0 \trusted; hoare model.
"""


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def is_lower(s: str) -> int:
    return s.islower()


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def is_dunder(s: str) -> int:
    if s.startswith("__") and s.endswith("__"):
        return 1
    return 0
