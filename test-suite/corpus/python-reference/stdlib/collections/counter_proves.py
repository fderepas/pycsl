"""collections.Counter — opaque counter object, modeled as non-negative int."""
# pycsl-flags: --no-proof
_ = 0  # anchor
from collections import Counter  # noqa: F401


#@ \trusted
#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
def make_counter(items: int) -> int:
    return Counter(items)


if __name__ == "__main__":
    pass
