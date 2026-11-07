"""multi_file_lib.r269_main_peer — route #269 R5 fixture for corpus 2892: `f` calls back into
the RUNNING program's `g` through `__main__`, closing a call cycle across the module boundary.
(Imported anywhere `__main__` has no `g` — the contract-truth harness — it returns 0.)"""
import __main__


#@ ensures \result == 0
#@ assigns \nothing
def f(k: int) -> int:
    if hasattr(__main__, "g"):
        return __main__.g(k)
    return 0
