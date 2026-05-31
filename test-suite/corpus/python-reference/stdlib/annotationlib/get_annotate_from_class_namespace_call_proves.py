"""Test annotationlib.get_annotate_from_class_namespace L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import annotationlib  # noqa: F401


#@ requires True
#@ ensures True
def use_get_annotate_from_class_namespace(x: int) -> int:
    return annotationlib.get_annotate_from_class_namespace(x)


if __name__ == "__main__":
    pass
