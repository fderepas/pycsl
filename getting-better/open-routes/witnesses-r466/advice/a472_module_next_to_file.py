"""Advice probe (route #472, PYCSL-R472-IMPORT-NOT-ON-TARGET-PATH): 'Put the module next to this
file' -- witness 7282's `import frontend` replaced by a module of the program. VERIFIES."""
import x1_mod472


#@ no_exception \all
#@ ensures \result == n
def f(n: int) -> int:
    return n
