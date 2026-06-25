# pycsl_lib/typ — pure-Python typing module
# cast: Modelled (identity). Rest: Stubbed.
# Union (typing-engagement ty1 / 25-1700-typing-spec-1): Modelled-for-identity.
#   The static plane (Module 5/6) desugars `Union[X, Y]`/`Optional[X]`/`X | Y`
#   annotations into a synthesized variant type_decl with per-arm VCs (C2/C3).
#   This runtime shim constructs the introspectable object and performs NO
#   validation (R1–R8, D4 no-blend). The `ensures \result == val` carries ONLY
#   the identity postcondition — it cannot discharge any static clause.


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


#@ ensures \result == val
def Union(x0, x1, val) -> int:
    return val


def overload(func):
    return func


def no_type_check(func):
    return func
