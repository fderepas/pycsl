r"""Test 1692 - ROUTE #197 control (gen #30): the repair is confined to UNKNOWN. When the object's record type IS known and genuinely does NOT declare the name, `getattr` really does return the default, and that faithful answer is exactly what route #22's gate was built to protect - so it still proves. Only the case where the model can establish neither presence NOR absence became opaque.
"""
from typing import Any

_ = 0  # anchor


class C:
    def __init__(self):
        self.a: int = 7

    #@ requires True
    #@ ensures \result == 1
    def peek(self) -> int:
        v = getattr(self, "zzz", 0)
        if v == 0:
            return 1
        return 2
