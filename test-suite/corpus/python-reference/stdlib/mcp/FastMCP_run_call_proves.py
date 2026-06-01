"""Test mcp.FastMCP_run L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import mcp  # noqa: F401


#@ requires True
#@ ensures True
def use_FastMCP_run(x: int) -> int:
    return mcp.FastMCP_run(x)


if __name__ == "__main__":
    pass
