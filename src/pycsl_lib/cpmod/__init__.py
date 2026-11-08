# pycsl_lib/cpmod — pure-Python copy module
# deepcopy: Modelled-hard (aliasing/cycles). Deferred until memory model supports it.
# (#49) INTEGER MODEL, stated in the signature: `obj: int`. Route #252 refuses an erased
# (unannotated) value flowing into the `-> int` return, because the model would re-apply
# int laws to it -- and for a non-int `\result == obj` is not even true of CPython (a
# plain instance's copy is `!=` its original under default identity `__eq__`). The
# identity contract is true exactly on the int domain this model covers.


class Error(Exception):
    pass


#@ ensures \result == obj
def deepcopy(obj: int) -> int:
    return obj


#@ ensures \result == obj
def copy(obj: int) -> int:
    return obj
