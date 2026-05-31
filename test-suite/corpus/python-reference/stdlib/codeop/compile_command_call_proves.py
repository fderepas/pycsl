"""Test codeop.compile_command L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import codeop  # noqa: F401


#@ requires True
#@ ensures True
def use_compile_command(x: int) -> int:
    return codeop.compile_command(x)


if __name__ == "__main__":
    pass
