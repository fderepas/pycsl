"""Test jsonschema.Draft202012Validator L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import jsonschema  # noqa: F401


#@ requires True
#@ ensures True
def use_Draft202012Validator(x: int) -> int:
    return jsonschema.Draft202012Validator(x)


if __name__ == "__main__":
    pass
