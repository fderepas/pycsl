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
# Final (typing-engagement ty1 / 27-0000-typing-spec-3): Modelled-for-identity.
#   The static plane (Module 5 + core_ir_semantic._check_final) treats
#   `Final[T]` as a write-restriction: write-once at the declaration (F1) or
#   __init__-only for instance attributes (F2), discharged by a syntactic
#   write-site check (degenerate HAPPY no-write confinement — NOT a VC). This
#   runtime shim constructs the introspectable `typing.Final` alias object and
#   performs NO validation (FR1–FR6, FD2 no-blend). It is explicitly NOT a
#   write-guard descriptor — introducing one would blend the planes (FR6). The
#   `ensures \result == val` carries ONLY the identity postcondition — the
#   static write-policy is NOT discharged by the shim (it is a semantic check,
#   invisible to the runtime).
# NoReturn (typing-engagement ty1 / 28-0000-typing-spec-4): Modelled-for-identity.
#   The static plane (Module 5 + Module 6 + core_ir_semantic) treats
#   `-> NoReturn` as a `false` postcondition (NR1): the function never returns
#   normally. Module 5 records the `is_noreturn` IR flag; Module 6 emits
#   `ensures { false }`; core_ir_semantic checks the body supports divergence
#   (NR2a) and flags dead successors (NR3); the non-vacuity gate exempts the
#   function (NR4). This runtime shim constructs the introspectable
#   `typing.NoReturn` alias object and performs NO validation (NR-R1–NR-R5,
#   NR-D2 no-blend). The runtime does NOT enforce divergence (NR-R3 — the
#   central negative sentence: the runtime does not enforce annotations).


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


#@ ensures \result == val
def Final(x0, x1, val) -> int:
    return val


# NoReturn (PEP 484) is a type marker, not a callable: it appears only in
# return annotations (`-> NoReturn`), never as a value. The shim provides the
# introspectable alias object (NR-R1/NR-R2) with NO enforcement (NR-R3). The
# static plane handles the `false` postcondition (NR1); the runtime plane does
# nothing (NR-D1/NR-D2 no-blend).
NoReturn = None


def overload(func):
    return func


def no_type_check(func):
    return func
