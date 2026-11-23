r"""Test 10401 -- route #327, CLASS site (expected FAIL, refused): the live witness of the
PYCSL-R327-IDENT-COLLISION raise "the classes '...' and '...' lower to ONE WhyML namespace"
in src/pycsl/pycsl.py. `Ab` and `AB` differ only in case; both are `@dataclass` classes with
one field and NO methods, so both lower to type declarations while no two functions share a
WhyML name (route #620, PYCSL-SEM-WHYML-NAME-CLASH, does not fire). Corpus 4308 (two classes
with `__init__` and `m`) is refused earlier by #620 since run #9 u65 (red team rt77 F3); this
file replaces it as the witness of the R327 class site (run #9 u68).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


@dataclass
class Ab:
    x: int


@dataclass
class AB:
    y: int


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    a = Ab(1)
    return a.x


if __name__ == "__main__":
    assert g() == 1, g()
