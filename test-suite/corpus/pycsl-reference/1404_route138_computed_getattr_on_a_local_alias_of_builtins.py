r"""Test 1404 — ROUTE #138: gen #26 scoped the computed-getattr-callee arm to a receiver named `__builtins__` or present in the file-wide `_nb_imported` set. `import builtins; b = builtins; getattr(b, "set" + "attr")(plainlib, "inc", plainlib.dec)` PROVED `plainlib.inc(3) == 4` while CPython returns 2. The rule is now keyed on the PATH: at module/class-body scope a `getattr` receiver must be a name this file can describe.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
import multi_file_lib.r119_plainlib as plainlib
import builtins

b = builtins
getattr(b, "set" + "attr")(plainlib, "inc", plainlib.dec)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)