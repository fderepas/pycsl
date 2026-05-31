"""Test annotationlib.annotations_to_string L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import annotationlib  # noqa: F401


#@ requires True
#@ ensures True
def use_annotations_to_string(x: int) -> int:
    return annotationlib.annotations_to_string(x)


if __name__ == "__main__":
    pass
