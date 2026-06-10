"""Test 0698 — strings: omitted `str` default fills `""`, not int 0 (10-1732-gap Gap 3).

DEMAND-DRIVER for Gap 3. The call-site default-fill loop lowered an omitted param's default
IR. A `None` default has IR `{"type":"None"}` which lowers to int `0`; applied to a `string`
param this is an ill-typed WhyML application ("expected type string, but is int"). The strmod
model worked around this by always passing `sep` explicitly.

The fix: when the omitted param's default IR is `{"type":"None"}` AND the param's WhyML type
(from the newly-wired by-name map) is non-int, fill the faithful zero (`""` for string, `0.0`
for real) instead. A genuine typed default (e.g. `sep: str = " "`) has IR `{"type":"String"}`
and falls through unchanged.

STATUS — **PROVES**. `use` calls `h(s)` with `sep` omitted; `sep` is filled `""` (string),
so the application type-checks and the `\str_length(\result) >= 0` postcondition discharges."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 0
#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def h(s: str, sep: str = None) -> str:
    return s                  # body ignores sep; the point is the call-site fill type

#@ requires \str_length(s) >= 0
#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def use(s: str) -> str:
    return h(s)               # sep omitted -> filled "" (string), NOT int 0

if __name__ == "__main__":
    print("PASS")
