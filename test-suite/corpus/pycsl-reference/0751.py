"""Test 0751 — PyCSL Annotation Reference (local str→str dict + str(x).lower()).

Two small recognizers: (1) a LOCAL dict literal with all-string values (`table = {"int":"i",...}`)
is a `dict[_, str]`, so `table[k]` reads a `string` (default "") not the int default; (2) `str(x)` is
string-typed, so `str(x).lower()` recognizes as a faithful string-value method (`str_lower_op`) rather
than an opaque scalar op."""
from typing import Dict
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class Sorter:
    depth: int = 0

    #@ requires True
    #@ ensures True
    def sort_of(self, name: str) -> str:
        table = {"int": "scalar", "str": "text", "list": "seq"}
        if name in table:
            return table[name]
        return str(name).lower()
