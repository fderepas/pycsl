"""Test annotationlib.call_annotate_function L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import annotationlib  # noqa: F401


#@ requires True
#@ ensures True
def use_call_annotate_function(x: int) -> int:
    return annotationlib.call_annotate_function(x)


if __name__ == "__main__":
    pass
