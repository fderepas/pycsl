"""Test json.JSONDecoder_decode L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import json  # noqa: F401


#@ requires True
#@ ensures True
def use_JSONDecoder_decode(x: int) -> int:
    return json.JSONDecoder_decode(x)


if __name__ == "__main__":
    pass
