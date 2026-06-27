"""Static gate P3 — non-conformance: a class missing a member is a static error.

Spec clause P3 (§1.1): "A class C that lacks a member of P ... does NOT conform
to P. ... A program that treats such a C value as a P is a static type error."

This driver exercises the MISSING-MEMBER rejection: `Circle` declares
`#@ conforms_to Drawable` but does NOT provide a `draw` method. PyCSL must
reject this at the front-end (a `PYCSLSEMANTICERROR`), before any VC is emitted.

Expected (from spec): the file is REJECTED with a semantic error —
"class 'Circle' ... does not provide member 'draw'". This is the P3
non-conformance rejection (a class missing a member fails conformance).
"""

# pycsl-expected: FAIL

from typing import Protocol


class Drawable(Protocol):
    #@ ensures \result >= 0
    def draw(self) -> int: ...


#@ conforms_to Drawable
class Circle:
    pass


if __name__ == "__main__":
    print("PASS")
