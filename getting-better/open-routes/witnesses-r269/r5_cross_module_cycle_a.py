r"""Route #269 R5 witness (pair with r5_cross_module_cycle_b.py): `g` (here) and `f` (there)
call each other ACROSS the module boundary. Each unit sees the other's function only as an
imported trusted stub with its `ensures`, so each PROVED `\result == 0` at 8b0bfbbd, each
assuming the other circularly. CPython (run this file): RecursionError. Not a corpus file:
a corpus driver `NNNN_*.py` cannot be the target of an `import`. Now refused in both units
(PYCSL-SEM-CROSS-MODULE-RECURSION).
"""
import r5_cross_module_cycle_b

#@ ensures \result == 0
#@ assigns \nothing
def g(k: int) -> int:
    return r5_cross_module_cycle_b.f(k)

if __name__ == "__main__":
    import sys; sys.setrecursionlimit(100)
    try:
        print(g(1))
    except RecursionError:
        print("RecursionError")
