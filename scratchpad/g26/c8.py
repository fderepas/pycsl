r"""C8 — carrier: `import builtins; builtins.setattr(...)` at module scope."""
_ = 0  # anchor
import builtins
import multi_file_lib.r119_plainlib as plainlib

builtins.setattr(plainlib, "inc", plainlib.dec)


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    return plainlib.inc(3)
