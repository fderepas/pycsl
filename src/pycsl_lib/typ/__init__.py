# pycsl_lib/typ — pure-Python typing module
# cast: Modelled (identity). Rest: Stubbed.
# Union (typing-engagement ty1 / 25-1700-typing-spec-1): Modelled-for-identity.
#   The static plane (Module 5/6) desugars `Union[X, Y]`/`Optional[X]`/`X | Y`
#   annotations into a synthesized variant type_decl with per-arm VCs (C2/C3).
#   This runtime shim constructs the introspectable object and performs NO
#   validation (R1–R8, D4 no-blend). The `ensures \result == val` carries ONLY
#   the identity postcondition — it cannot discharge any static clause.
# Literal (typing-engagement ty1 / 26-0000-typing-spec-2): Modelled-for-identity.
#   The static plane (Module 5) desugars `Literal[v1, ..., vn]` annotations into
#   a ground `requires { x = v1 \/ ... \/ x = vn }` clause (L1) — a finite
#   disjunction of concrete-value equalities, discharged by SMT. This runtime
#   shim constructs the introspectable `typing.Literal` alias object and performs
#   NO validation (LR1–LR8, LD3 no-blend). The `ensures \result == val` carries
#   ONLY the identity postcondition — the static L1 value-set obligation is NOT
#   discharged by the shim (it is a precondition VC, invisible to the runtime).


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


#@ ensures \result == val
def Literal(x0, x1, val) -> int:
    return val


def overload(func):
    return func


def no_type_check(func):
    return func
