# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL
"""1278 — (#49) ROUTE #98 EXPLOIT ARM: route #96's frame repair was keyed on the
EMITTED parameter name while the `assigns` clause carries the SOURCE name.

`_current_array_param_names` is built in `module6_whyml/functions.py` by regexing the
ALREADY-EMITTED signature (`re.findall(r"\((\w+)\s*:\s*array\b", args_str)`), so it holds
post-`whyml_ident` names. `whyml_ident` prefixes every WhyML reserved word with `py_`, and
`WHYML_RESERVED` contains `model` — an entirely ordinary Python parameter name (also
`range`, `check`, `label`, `result`, `old`, `ref`, `float`, `to`, `by`, `type`).
`_emit_frame_condition` then tested the SOURCE name `model` for membership in
`{"py_model"}`, the membership failed, and the emitted val carried NO `writes` at all:

    val scramble (py_model: array int) (n: int) : int
      requires { (n >= 0) }

Why3 therefore treated the stub as PURE. MEASURED AT a32ec69e: this file PROVED
`\result == 7`, while CPython running the stub's declared behaviour returns 0. Renaming the
parameter to `a` — changing nothing else — made the `writes { a }` clause appear and the
same exploit was refused. The ONLY difference was the identifier.

>>> A CARRIER SURVIVING A REPAIR IS A SECOND ROUTE, NOT A FAILED REPAIR.

REPAIRED by putting the region base through `whyml_ident` BEFORE the membership test and
appending the EMITTED name, so the two names are compared in ONE name space. This file must
FAIL.
"""


#@ requires n >= 0
#@ assigns model[0..n]
#@ \trusted reviewer: route98
def scramble(model: list, n: int) -> int:
    model[0] = 0
    return 0


#@ requires \length(arr) > 3
#@ requires arr[0] == 7
#@ ensures \result == 7
def driver(arr: list) -> int:
    scramble(arr, 1)
    return arr[0]
