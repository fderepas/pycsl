"""Test mcp.FastMCP L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import mcp  # noqa: F401


#@ requires True
#@ ensures True
def use_FastMCP(x: int) -> int:
    return mcp.FastMCP(x)


if __name__ == "__main__":
    pass
