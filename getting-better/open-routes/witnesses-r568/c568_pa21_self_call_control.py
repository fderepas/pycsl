"""probe pa21 CONTROL: the pa16 caller as a METHOD calling self.m on a class with NO emitted record (the self-arm's coarse `_pyobj_state` fallback is in the val frame). Expected: the false `\result == 1` is NOT proved."""
from typing import Any
def mutable_state(cls):
    return cls

@mutable_state
class C:
    #@ \trusted reviewer: probe
    #@ requires True
    #@ ensures True
    #@ assigns self.flag
    def __init__(self) -> None:
        pass

    #@ requires True
    #@ ensures True
    #@ assigns self.flag
    def m(self, v: int) -> None:
        self.flag = v

    #@ requires True
    #@ ensures \result == 1
    #@ assigns self.flag
    def caller(self, o: Any) -> int:
        self.m(0)
        x = getattr(o, "flag", 0)
        self.m(5)
        y = getattr(o, "flag", 0)
        if x or not y:
            return 1
        return 2

if __name__ == "__main__":
    k = C()
    print(k.caller(k))
