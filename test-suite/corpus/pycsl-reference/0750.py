"""Test 0750 — PyCSL Annotation Reference (class-constant dict modeling).

A class-level constant lookup table typed `Dict[str, str]` (`TAGS = {"int": "tag_int", ...}`) is
modelled as an abstract `map int (option string)` field: membership `k in self.TAGS` reads back a
bool (str-hashed key) and subscript `self.TAGS[k]` reads back a `string`. The actual entries stay
unmodelled (sound — the type-safety+frame contract needs only the result TYPES, not the tag values)."""
from typing import Dict
from dataclasses import dataclass


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class Tagger:
    depth: int = 0
    # a class-constant lookup table (annotation makes it a modelled Dict field; the literal
    # entries stay unmodelled — the abstract `map int (option string)`)
    TAGS: Dict[str, str] = None

    #@ requires True
    #@ ensures True
    def tag_of(self, name: str) -> str:
        if name in self.TAGS:
            return self.TAGS[name]
        return ""
