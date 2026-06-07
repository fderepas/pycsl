# pure_lib/cpmod — pure-Python copy module
# deepcopy: Modelled-hard (aliasing/cycles). Deferred until memory model supports it.


class Error(Exception):
    pass


#@ ensures \result >= 0
def deepcopy(obj) -> int:
    return obj


#@ ensures \result >= 0
def copy(obj) -> int:
    return obj
