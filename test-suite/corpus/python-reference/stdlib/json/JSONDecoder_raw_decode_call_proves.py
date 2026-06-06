"""Test json.JSONDecoder_raw_decode L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import json  # noqa: F401


#@ requires True
#@ ensures True
def use_JSONDecoder_raw_decode(x: int) -> int:
    return json.JSONDecoder_raw_decode(x)


if __name__ == "__main__":
    pass
