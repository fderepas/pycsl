"""Advice probe (route #466, the module-attribute message): 'Bind the name unconditionally at the
module's top level' -- witness 7267's helper binds `g` outside the `if False:`. VERIFIES."""
import x1_hb466 as h


#@ no_exception \all
#@ ensures \result == n
def f(n: int) -> int:
    return h.g(n)
