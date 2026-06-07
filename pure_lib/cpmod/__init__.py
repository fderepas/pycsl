# pure_lib/cpmod — pure-Python copy module
# deepcopy: Modelled-hard (aliasing/cycles). Deferred until memory model supports it.


class Error(Exception):
    pass


#@ ensures \result == obj
def deepcopy(obj) -> int:
    return obj


#@ ensures \result == obj
def copy(obj) -> int:
    return obj
