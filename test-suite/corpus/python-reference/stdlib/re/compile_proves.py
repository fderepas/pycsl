"""re.compile() — returns a Pattern object; result is an opaque value."""
# pycsl-flags: --no-proof
_ = 0  # anchor
import re  # noqa: F401


#@ \trusted
#@ requires True
#@ ensures \result >= 0
#@ assigns \nothing
def build_pattern(p: int) -> int:
    return re.compile(p)


if __name__ == "__main__":
    pass
