"""Test io.text_encoding L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import io  # noqa: F401


#@ requires True
#@ ensures True
def use_text_encoding(x: int) -> int:
    return io.text_encoding(x)


if __name__ == "__main__":
    pass
