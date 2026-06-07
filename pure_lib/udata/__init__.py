# pure_lib/udata — pure-Python unicodedata module
# Specified: Unicode database axiomatized (name→char, normalize idempotent).
# TCB: name/normalization facts are assumed, not proven.


#@ ensures \result >= 0
def lookup(name) -> int:
    return 0


#@ requires s >= 0
#@ ensures \result >= 0
def normalize(form, s) -> int:
    return s
