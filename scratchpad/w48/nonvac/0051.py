"""Test 0051 — Python Reference 3.2.8.2: Instance methods"""
_ = 0  # anchor


class Counter:
    #@ requires True
    #@ ensures self.n == 0
    #@ assigns self.n
    def __init__(self) -> None:
        self.n = 0

    #@ requires True
    #@ ensures self.n == \old(self.n) + 1
    #@ assigns self.n
    def bump(self) -> None:
        self.n = self.n + 1

    #@ requires True
    #@ ensures \result == self.n
    #@ assigns \nothing
    def get(self) -> int:
        return self.n


#@ ensures \result == 0
#@ assigns \nothing
def test_instance_methods() -> int:
    """Ref 3.2.8.2: an instance method combines a class, an instance and a function — the
    instance is passed as the first argument, so a call through the instance operates on
    THAT instance's state and successive calls COMPOSE. The contract on `bump` is
    relational (`self.n == \\old(self.n) + 1`), so the two calls below can only reach 2 if
    the emitter really threads the receiver's state through both. Previously the whole body
    was `return 0` and the postcondition was discharged by the tail `return` alone,
    exercising no method and no instance (relaunch #46,
    `bin/check-vacuous-drivers.py`)."""
    c = Counter()
    c.bump()
    c.bump()
    if c.get() == 3:
        return 0
    return 1


if __name__ == "__main__":
    assert test_instance_methods() == 0
