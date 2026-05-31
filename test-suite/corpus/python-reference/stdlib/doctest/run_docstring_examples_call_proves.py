"""Test doctest.run_docstring_examples L5 — positive: caller exploits ensures."""
# pycsl-flags: --no-proof
# pycsl-expected: PASS
_ = 0  # anchor
import doctest  # noqa: F401


#@ requires True
#@ ensures True
def use_run_docstring_examples(x: int) -> int:
    return doctest.run_docstring_examples(x)


if __name__ == "__main__":
    pass
