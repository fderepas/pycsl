r"""Route #269 R5 witness, second half (see r5_cross_module_cycle_a.py)."""
import r5_cross_module_cycle_a

#@ ensures \result == 0
#@ assigns \nothing
def f(k: int) -> int:
    return r5_cross_module_cycle_a.g(k)
