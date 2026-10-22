from typing import Any, Dict, List

PyVal = Any


class E:
    def __init__(self) -> None:
        self.program_ir: Dict[str, PyVal] = {}

    #@ assigns self.program_ir
    def top(self, d: Dict[str, PyVal]) -> None:
        self.program_ir["constructors"] = d.get("x")
