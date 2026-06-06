"""Test 0555 — typed quantifier binder over a #@ datatype (quantification P1).

The flagship for `quantification.md` P1, and the spec's §11 type-soundness hole:
a `\forall` whose binder is a declared `#@ datatype`. Today PyCSL lowers EVERY
quantifier binder to `: int` (`module6_whyml/expressions.py`, the Forall/Exists
arm is hard-wired), so `\forall c: Color; …` emits `forall c : int.` and then
applies datatype observers to an `int` — front-end green, **Why3 type-error**.
This is the false-green hole the spec names.

PASSES under P1: a typed binder `c: Color` resolves against the module's
`#@ datatype` registry and lowers to `forall c : color.`, so the quantified fact
`rank(c) in [0, 2]` type-checks and discharges (Why3 case-splits the finite ADT).

Negative twins for this phase: 0556 (unresolved binder type → hard Module4 error,
not a silent `int`) and 0557 (bare untyped binder used as a datatype value).
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ datatype Color = Red | Green | Blue


#@ ensures \result >= 0 and \result <= 2
#@ assigns \nothing
def rank(c: Color) -> int:
    match c:
        case Red():
            return 0
        case Green():
            return 1
        case Blue():
            return 2


#@ ensures \result >= 0 and \result <= 2
#@ ensures \forall c: Color; rank(c) >= 0 and rank(c) <= 2
#@ assigns \nothing
def all_ranks_bounded(x: Color) -> int:
    return rank(x)
