r"""Test 7596 -- route #485 control (expected PASS): a dunder-style name the file BINDS (`__version__ = 3`) is a module-level int this file computed, not an implicit module global, so `__version__ + n` keeps its int model under the never-bound origin rule.
"""
# pycsl-expected: PASS

__version__ = 3


#@ requires n >= 0
#@ ensures \result == n + 3
#@ no_exception \all
def f(n: int) -> int:
    return __version__ + n


if __name__ == "__main__":
    print("result", f(1))
