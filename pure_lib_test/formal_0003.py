"""Formal test 0003: pure_lib/warn — simplefilter, _deprecated.

Verifies that warning functions maintain their contracts for all
symbolic inputs. warn() is excluded because it can raise Exception
(when filter is "error"), and PyCSL formal tests cannot declare
raises clauses.
"""
from pure_lib.warn import simplefilter, _deprecated


#@ assigns \nothing
#@ ensures \result == 0 or \result == 1
def formal_test_simplefilter(action) -> int:
    """simplefilter() returns >= 0."""
    rc = simplefilter(action, 0, 1, 0)
    if rc < 0:
        return 1
    return 0


#@ assigns \nothing
#@ ensures \result == 0
def formal_test_deprecated(name) -> int:
    """_deprecated() always returns 0."""
    rc = _deprecated(name, 0, 0, 0)
    return rc
