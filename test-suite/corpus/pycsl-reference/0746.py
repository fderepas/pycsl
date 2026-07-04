"""Test 0746 — PyCSL Annotation Reference (nested dict-of-lists: Dict[str, List[str]]).

Exercises the #15 fix: a `Dict[str, List[T]]` field lowers to `map int (option (seq T))` (was
flattened to `map int (option int)`), so `.get(k, [])` reads back a `seq string` (empty-seq default)
and a local bound to it (`fp`) is a `seq string` — its `len` is `Seq.length`, no int leak."""
from dataclasses import dataclass
from typing import Dict, List


def mutable_state(cls):
    return cls


@mutable_state
@dataclass
class Registry:
    formal_params: Dict[str, List[str]] = None

    #@ requires True
    #@ ensures \result >= 0
    def arity(self, name: str) -> int:
        fp = self.formal_params.get(name, [])
        return len(fp)


if __name__ == "__main__":
    r = Registry()
    r.formal_params = {}
    assert r.arity("f") == 0
