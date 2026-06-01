"""Test jsonschema.RefResolver L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import jsonschema  # noqa: F401


#@ requires True
#@ ensures True
def use_RefResolver(x: int) -> int:
    return jsonschema.RefResolver(x)


if __name__ == "__main__":
    pass
