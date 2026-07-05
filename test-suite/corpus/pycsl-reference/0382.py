"""Test 0382 — interprocedural ambient mode: unannotated callee.

The callee `legacy_divide` has no annotations beyond the basic
contracts. The caller declares `no_exception ZeroDivisionError`. In
the default (ambient) mode the caller is not penalised for calling an
unannotated callee — backward-compatibility per workplan §11.3.
"""
_ = 0  # anchor
#@ requires n != 0
#@ ensures \result == 256 // n
#@ assigns \nothing
def legacy_divide(n: int) -> int:
    return 256 // n

#@ requires n != 0
#@ ensures \result == 256 // n
#@ assigns \nothing
#@ no_exception ZeroDivisionError
def caller(n: int) -> int:
    return legacy_divide(n)


if __name__ == "__main__":
    assert caller(8) == 32
