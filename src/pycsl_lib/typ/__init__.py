# pycsl_lib/typ — pure-Python typing module
# cast: Modelled (identity). Rest: Stubbed.


#@ ensures \result == val
def cast(typ, val) -> int:
    return val


#@ ensures \result >= 0
def get_type_hints(obj) -> int:
    return 0


#@ ensures \result >= 0
def get_origin(tp) -> int:
    return 0


#@ ensures \result >= 0
def get_args(tp) -> int:
    return 0


def overload(func):
    return func


def no_type_check(func):
    return func
