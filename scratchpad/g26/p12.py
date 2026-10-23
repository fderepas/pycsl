r"""P12 — #136 sibling: `eval` with a walrus BINDS a name; exec_splice's docstring claims
eval/compile/ast.parse "do not inject names"."""
_ = 0  # anchor
N = 3
eval("(N := 5)")


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return N
