"""Test 1268 — route #96, the `\abstract` ARM of the same disjunction, measured separately.

`emit_as_val = func_trusted or func_abstract or func_trusted_parent`, so the dropped frame was
never specific to `\trusted`. This file is 1267 with `#@ \abstract` in place of `#@ \trusted`
and it PROVED the same false postcondition before the repair. Keeping BOTH arms as standing
witnesses means a future narrowing of the fix to only one of them turns this file red.
"""
# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL

#@ requires n >= 0
#@ requires \length(a) > n + 1
#@ assigns a[0..n]
#@ \abstract
def scramble(a: list, n: int) -> int:
    ...


#@ requires \length(arr) > 3
#@ requires arr[0] == 7
#@ ensures \result == 7
def driver(arr: list) -> int:
    scramble(arr, 1)
    return arr[0]
