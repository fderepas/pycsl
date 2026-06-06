"""typing.List used as a type alias. Trivial — just exercises import resolution."""
# pycsl-flags: --no-proof
_ = 0  # anchor
from typing import List  # noqa: F401


#@ requires \length(items) >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def first_or_zero(items: list) -> int:
    if len(items) > 0:
        return items[0]
    return 0


if __name__ == "__main__":
    assert first_or_zero([42, 7]) == 42
    assert first_or_zero([]) == 0
