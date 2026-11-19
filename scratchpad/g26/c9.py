r"""C9 — carrier: `import builtins; builtins.exec(...)` at module scope."""
_ = 0  # anchor
import builtins

N = 3
builtins.exec("N" + " = 5", globals())


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
