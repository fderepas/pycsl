"""Test annotationlib.call_evaluate_function L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import annotationlib  # noqa: F401


#@ requires True
#@ ensures True
def use_call_evaluate_function(x: int) -> int:
    return annotationlib.call_evaluate_function(x)


if __name__ == "__main__":
    pass
