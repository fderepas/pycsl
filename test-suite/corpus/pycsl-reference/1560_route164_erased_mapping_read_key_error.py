r"""Test 1560 - ROUTE #164 (gen #29, carrier of its own #159 KeyError fence, which covered only a dict LITERAL): `os.environ[\"<absent>\"]` lowered to an erased `subscript_get` with no KeyError obligation and PROVED `no_exception KeyError`; CPython raises. Every erased read now carries the unprovable obligation.
"""
# pycsl-expected: FAIL
import os
_ = 0  # anchor


#@ no_exception KeyError
def probe() -> int:
    v = os.environ["PYCSL_SURELY_ABSENT_KEY_29"]
    return len(v)

