"""Formal test for Phase 6+7 modules: ctxlib (nullcontext),
cpmod (deepcopy, copy). sha256 excluded: class-return type mismatch (R13)."""

from pycsl_lib.ctxlib import nullcontext
from pycsl_lib.cpmod import deepcopy, copy


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def formal_test_nullcontext_exit(nc) -> int:
    e = nc.__exit__(0, 0, 0)
    if e != 0:
        return 1
    return 0


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def formal_test_deepcopy(val) -> int:
    r = deepcopy(val)
    if r != val:
        return 1
    return 0


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def formal_test_copy(val) -> int:
    r = copy(val)
    if r != val:
        return 1
    return 0
