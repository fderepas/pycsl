r"""Test 1395 — ROUTE #136: #127's rules name `__builtins__`, not the `builtins` MODULE. `import builtins; builtins.setattr(plainlib, "inc", plainlib.dec)` PROVED `plainlib.inc(3) == 4` while CPython returns 2. A namespace builtin reached as an ATTRIBUTE is now refused (census over the five trees: 0 sites).
"""
# pycsl-expected: FAIL
_ = 0  # anchor
import builtins
import multi_file_lib.r119_plainlib as plainlib

builtins.setattr(plainlib, "inc", plainlib.dec)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
