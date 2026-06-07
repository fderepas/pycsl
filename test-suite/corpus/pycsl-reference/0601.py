"""Test 0601 — negative: an array/list of tuples is rejected, not silently hashed (0442.md C3).

PyCSL has no faithful `array (tuple)` model. Previously a list of tuples silently collapsed each
tuple element to an int hash (`Array.make 2 (769300025) …`), losing all structure — unsound. It
is now an explicit hard error (use parallel arrays). This negative test confirms the rejection
(no silent int-flattening), per the no-more-int doctrine.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \length(\result) == 2
#@ assigns \nothing
def pairs() -> list:
    return [(1, 2), (3, 4)]
