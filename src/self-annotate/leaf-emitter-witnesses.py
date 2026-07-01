"""leaf-emitter-witnesses.py — Ceiling-A evidence for semantic-ceiling-plan.md §12.

These are body-faithful contracts for the *leaf* WhyML-emitter shapes (constant
strings prefixed by `indent`, no reflection / no state / no sibling calls). They
PROVE with `pycsl`, demonstrating that Ceiling A (the modeling wall) is genuinely
*clear for non-reflective emitter code* — B2's f-string→str_concat fix makes the
leaf `_handle_*` bodies verifiable against an exact-string postcondition.

The compositional handlers (assign/if/while/for/…) are a different story: they
bottom out in `_expr_to_whyml` (`Dict[str, Any]`, reflective, unmigrated), which
is ceiling-blocked until the expression subsystem is migrated to typed ExprIR
("Phase-B-expr"). See semantic-ceiling-plan.md §12.

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/leaf-emitter-witnesses.py
"""


#@ ensures \result == indent + "raise PyCSL_Continue"
def handle_continue(indent: str) -> str:
    return f"{indent}raise PyCSL_Continue"


#@ ensures \result == indent + "raise PyCSL_Break"
def handle_break(indent: str) -> str:
    return f"{indent}raise PyCSL_Break"


#@ ensures \result == indent + "()"
def handle_pass(indent: str) -> str:
    return f"{indent}()"


#@ ensures \result == indent + "raise " + exc
def handle_raise(indent: str, exc: str) -> str:
    return f"{indent}raise {exc}"
