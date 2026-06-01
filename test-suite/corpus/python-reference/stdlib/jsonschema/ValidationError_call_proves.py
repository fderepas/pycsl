"""Test jsonschema.ValidationError L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import jsonschema  # noqa: F401


#@ requires True
#@ ensures True
def use_ValidationError(x: int) -> int:
    return jsonschema.ValidationError(x)


if __name__ == "__main__":
    pass
