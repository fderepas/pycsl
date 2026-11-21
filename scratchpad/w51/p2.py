# pycsl-flags: --memory-model hoare
# ROUTE #51 shape (d) PROBE: the FIELD case (q5) WITHOUT @mutable_state — localises the gate.
from dataclasses import dataclass


@dataclass
class C:
    name: str = ""

    #@ requires True
    #@ ensures \result == 7
    #@ assigns \nothing
    def probe(self) -> int:
        if self.name is None:
            return 0
        return 7


if __name__ == "__main__":
    o = C()
    o.name = None
    assert o.probe() == 0
