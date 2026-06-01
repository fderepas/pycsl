"""Test libcst.parse_statement L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import libcst  # noqa: F401


#@ requires True
#@ ensures True
def use_parse_statement(x: int) -> int:
    return libcst.parse_statement(x)


if __name__ == "__main__":
    pass
