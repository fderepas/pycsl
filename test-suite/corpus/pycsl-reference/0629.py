"""Test 0629 — build a list local by concat and RETURN it, proving the length (07-1705 P4).

A seq-modelled list local is built (`a += b`) then returned where the function's declared return
is `list` (`array int`). The seq→array boundary materialises a FRESH array (`materialize !a`),
so `\length(\result) == 5` proves end-to-end — build-by-concat then return, fully faithful.
"""
# pycsl-flags: --memory-model hoare


#@ ensures \length(\result) == 5
#@ assigns \nothing
def build() -> list:
    a = [1, 2, 3]
    b = [4, 5]
    a += b
    return a
