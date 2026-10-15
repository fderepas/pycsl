r"""Test 2220 — ch15 crash fix: `len(p.<f>)` on a RECORD PARAM whose class carries a
`List[<record>]` field (so `_record_array_fields`, a dict field -> element record, is
populated) is the ARRAY length. The emitter's record-param arm unioned that dict with the
`_str_array_record_fields` set via `dict | set` and raised `TypeError` (emitter crash on every
such program); the union is now over the field NAMES. CPython: `count(Parser([Tok(1)]))`
is 1. Expected PASS. False-claim twin: 2221.
"""
from dataclasses import dataclass
from typing import List


def mutable_state(cls):
    return cls


@dataclass
class Tok:
    kind: int


#@ class invariant 0 <= self.i
#@ class invariant self.i < \length(self.toks)
#@ class invariant \length(self.toks) >= 1
@mutable_state
class Parser:
    def __init__(self, toks: List[Tok]):
        self.toks: List[Tok] = toks
        self.i: int = 0


#@ ensures \result == len(p.toks)
#@ ensures \result >= 1
#@ assigns \nothing
def count(p: Parser) -> int:
    return len(p.toks)


if __name__ == "__main__":
    assert count(Parser([Tok(1)])) == 1
    assert count(Parser([Tok(1), Tok(2)])) == 2
