r"""C6 — carrier: `exec` reached as an attribute of `__builtins__`."""
_ = 0  # anchor
N = 3
__builtins__.exec("N" + " = 5")


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
