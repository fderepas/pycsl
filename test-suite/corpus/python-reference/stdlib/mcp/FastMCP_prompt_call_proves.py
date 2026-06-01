"""Test mcp.FastMCP_prompt L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import mcp  # noqa: F401


#@ requires True
#@ ensures True
def use_FastMCP_prompt(x: int) -> int:
    return mcp.FastMCP_prompt(x)


if __name__ == "__main__":
    pass
