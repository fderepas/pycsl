"""string-op-tier-map.py — A2 empirical tier map for a2-a3-plan.md §2.1/§9.

Which string operations the emitter uses can PyCSL prove body-faithful today?
Measured by probing each as a `#@`-annotated function (the leaf-emitter-witnesses
pattern). This file holds the Tier-F / already-handled ops that PROVE; the ones
that do NOT prove are listed in the trailing comment (they are the A2 work).

Run: PYTHONPATH=src/pycsl .venv/bin/python -m pycsl src/self-annotate/string-op-tier-map.py
"""


# Tier F — string concatenation is faithful (str_concat, Why3 `concat`).
#@ ensures \result == s + t
def op_concat(s: str, t: str) -> str:
    return s + t


# Handled — `.startswith` in a BODY lowers to `str_startswith_op` (a bool);
# provable against a bool-shape contract (the emitter uses it for dispatch).
#@ ensures \result == 0 or \result == 1
def op_startswith(s: str, p: str) -> bool:
    return s.startswith(p)


# Handled — `.endswith` likewise (str_endswith_op).
#@ ensures \result == 0 or \result == 1
def op_endswith(s: str, p: str) -> bool:
    return s.endswith(p)


# --- NOT modelable today (the A2 gap — Tier T, need audited length/shape prims) ---
#   .replace  : `\length(\result) >= 0` FAILS  (no result-length ensures)
#   .strip    : `\length(\result) <= \length(s)` FAILS
#   .split/.rsplit/.join/.lower/.upper/.decode/.encode : no model
#   len(s) -> \length(s) : FAILS (str-length in contract not connected)
#   \length(s + t) in a SPEC : PARSE ERROR (grammar can't nest concat in \length)
# => A2 requires extending PyCSL's string theory (audited length/shape prims for
#    the Tier-T ops) AND the contract grammar (string-method predicates in specs).
