"""Test doctest.script_from_examples L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import doctest  # noqa: F401


#@ requires True
#@ ensures True
def use_script_from_examples(x: int) -> int:
    return doctest.script_from_examples(x)


if __name__ == "__main__":
    pass
