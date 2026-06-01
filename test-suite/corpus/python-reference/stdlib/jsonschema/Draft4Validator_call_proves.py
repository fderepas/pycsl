"""Test jsonschema.Draft4Validator L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import jsonschema  # noqa: F401


#@ requires True
#@ ensures True
def use_Draft4Validator(x: int) -> int:
    return jsonschema.Draft4Validator(x)


if __name__ == "__main__":
    pass
