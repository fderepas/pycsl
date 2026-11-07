r"""P1 — #132 carrier: `set((...))` tuple-arg str-set literal is folded by
collect_module_const_str_sets but the #132 escape arm only recognises ast.Set."""
_ = 0  # anchor
XS = set(("a", "b"))
XS.add("c")


#@ ensures \result == False
#@ assigns \nothing
def has_c() -> bool:
    return "c" in XS
