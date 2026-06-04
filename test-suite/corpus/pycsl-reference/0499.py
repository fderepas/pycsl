"""Test 0499 — collections: Counter as a count map (dict model).

`Counter()` reduces to the `map int (option int)` model: a missing count reads as 0, so an
explicit increment `c[k] = c[k] + 1` raises the count by one. Here a single increment from the
empty counter gives `c[5] == 1`. (The augmented form `c[k] += 1` is exercised by 0500.)
`most_common` / ranking / ordering are out of scope."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from collections import Counter


#@ ensures \result == 1
def count_one() -> int:
    c = Counter()
    c[5] = c[5] + 1
    return c[5]
