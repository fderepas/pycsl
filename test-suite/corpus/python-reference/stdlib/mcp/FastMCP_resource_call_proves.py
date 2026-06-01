"""Test mcp.FastMCP_resource L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import mcp  # noqa: F401


#@ requires True
#@ ensures True
def use_FastMCP_resource(x: int) -> int:
    return mcp.FastMCP_resource(x)


if __name__ == "__main__":
    pass
