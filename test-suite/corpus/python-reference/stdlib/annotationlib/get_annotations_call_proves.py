"""Test annotationlib.get_annotations L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import annotationlib  # noqa: F401


#@ requires True
#@ ensures True
def use_get_annotations(x: int) -> int:
    return annotationlib.get_annotations(x)


if __name__ == "__main__":
    pass
