"""Test 0476 — strings: __ne__ (`s != t`, content inequality).

Content inequality on runtime `str`. PROVES as of strings-plan Stage 2: `!=` is the
negation of the string-equality bridge (`not (str_eq_op a b)`) in a program context, and
the polymorphic `<>` in a spec. If-form for the same reason as 0475 (comparison-as-return
is a pre-existing, string-orthogonal gap)."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures (s != t) ==> \result == 1
#@ ensures (s == t) ==> \result == 0
#@ assigns \nothing
def strne(s: str, t: str) -> int:
    if s != t:
        return 1
    return 0
