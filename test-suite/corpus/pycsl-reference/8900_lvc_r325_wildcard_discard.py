r"""Test 8900 -- lvC R325 wildcard (expected PASS): a DISCARDED opaque call (`warnings.warn(..)` as a
statement lowers to `let _ = (warnings_warn_1 ..) in ()`) in a function that ALSO lowers a membership
test to the pattern match `match Map.get s k with Some _ -> true | None -> false end`. In WhyML `_` is the
wildcard PATTERN, never a readable variable, so the `Some _` arm is not a use of the discarded value. At
base route #325's scanner read that wildcard as the discarded local `_` "used as an integer" and refused
the whole file. The warn is still the opaque, unconstrained call it was; nothing is claimed about it.
Twins: 8901 / 8902 / 8903 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
import warnings


#@ ensures \result == n
#@ assigns \nothing
def warn_if_member(d: dict, seen: set, n: int) -> int:
    k = d.get("name", 0)
    if k in seen:
        warnings.warn("member")
    return n


if __name__ == "__main__":
    r = warn_if_member({"name": 3}, {3}, 7)
    print("VIOLATION contract" if r != 7 else "result", r)
