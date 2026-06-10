"""Test 0699 — strings: IMPORTED str-stub Gaps 2 & 3 end-to-end (10-1732-gap R2).

The REAL strmod shape: `capwords` is an IMPORTED `\trusted` `str`-returning stub with a
defaulted `str` param (mirrors `strmod.capwords`). This driver exercises BOTH fixes through
the import path:

  - Gap 2: `len(capwords(s))` taken DIRECTLY routes to str_length_op — requires the imported
    callee's WhyML return type (`string`) to be in `_module_method_return_types`.
  - Gap 3: `capwords(s)` with `sep` omitted fills `""` (string), not int 0 — requires the
    imported callee's by-name WhyML param types to be in `_module_method_param_whyml_types`.

Both maps are built from `funcs_for_maps`, which includes injected imported `\trusted` stubs
(ir_resolve._inject_functions copies the full dependency IR — formal_params, symbol_table,
return_annotation — into ir_data['functions']). So no extra import-threading was needed.

STATUS — **PROVES**. `cap_len` discharges `\result >= 0` from str_length_op over the imported
call; `cap_default` discharges `\str_length(\result) >= 0` after the omitted `sep` is filled
`""` so the imported application type-checks."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from multi_file_lib.strmod_stub import capwords

#@ requires \str_length(s) >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def cap_len(s: str) -> int:
    return len(capwords(s))         # Gap 2: imported str call -> str_length_op

#@ requires \str_length(s) >= 0
#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def cap_default(s: str) -> str:
    return capwords(s)              # Gap 3: sep omitted -> filled "" (imported stub)

if __name__ == "__main__":
    print("PASS")
