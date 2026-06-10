"""multi_file_lib.strmod_stub — fixture for 10-1732-gap R2 (imported-stub Gaps 2 & 3).

Mirrors the real `strmod.capwords` shape: a `\trusted` `str`-returning function with a
defaulted `str` parameter (`sep`). Imported by 0699 so the Gap-2 (`len(<imported str call>)`)
and Gap-3 (omitted imported str default) fixes are exercised through the IMPORT path — i.e.
that imported callees enter the WhyML return-type / by-name param-type maps that the fixes key
on. `sep` defaults to `None` (IR `{"type":"None"}`), the precise sentinel Gap 3 corrects.
"""
_ = 0  # anchor


#@ \trusted
#@ requires \str_length(s) >= 0
#@ ensures \str_length(\result) >= 0
#@ assigns \nothing
def capwords(s: str, sep: str = None) -> str:
    return s
