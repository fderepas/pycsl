"""Test annotationlib.type_repr L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import annotationlib  # noqa: F401


#@ requires True
#@ ensures True
def use_type_repr(x: int) -> int:
    return annotationlib.type_repr(x)


if __name__ == "__main__":
    pass
