"""Test 0490 — strings: __getitem__ by index (`s[i]`).

Indexing a string yields a single character, which in the Why3 string model (no char type)
is the length-1 substring `String.substring s i 1`. PROVES as of strings-plan Stage 2: `s[i]`
reuses the `str_sub_op` bridge with len=1, so the length-1 postcondition follows from the
bridge's baked-in length lemma under the in-bounds guard."""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ requires \str_length(s) >= 1
#@ ensures \str_length(\result) == 1
#@ assigns \nothing
def first_char(s: str) -> str:
    return s[0]
