"""Test json.JSONEncoder_encode L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import json  # noqa: F401


#@ requires True
#@ ensures True
def use_JSONEncoder_encode(x: int) -> int:
    return json.JSONEncoder_encode(x)


if __name__ == "__main__":
    pass
