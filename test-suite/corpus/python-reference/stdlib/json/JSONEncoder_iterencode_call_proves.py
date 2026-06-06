"""Test json.JSONEncoder_iterencode L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import json  # noqa: F401


#@ requires True
#@ ensures True
def use_JSONEncoder_iterencode(x: int) -> int:
    return json.JSONEncoder_iterencode(x)


if __name__ == "__main__":
    pass
