"""Test json.JSONEncoder_default L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import json  # noqa: F401


#@ requires True
#@ ensures True
def use_JSONEncoder_default(x: int) -> int:
    return json.JSONEncoder_default(x)


if __name__ == "__main__":
    pass
