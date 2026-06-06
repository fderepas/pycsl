"""json.dumps(obj) — returns string; modeled as non-negative integer."""
# pycsl-flags: --no-proof
_ = 0  # anchor
import json  # noqa: F401


#@ \trusted
#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
def encode(obj: int) -> int:
    return json.dumps(obj)


if __name__ == "__main__":
    pass
