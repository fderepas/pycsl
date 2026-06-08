"""Test 0641 — `literal_eval` of a constant string literal is faithful (07-1839 P5c)."""
# pycsl-flags: --memory-model hoare


#@ ensures \result == "hi"
#@ assigns \nothing
def f() -> str:
    return ast.literal_eval('"hi"')
