"""Test 0058 — Python Reference 3.2.8.9: Class Instances"""
_ = 0  # anchor


class Box:
    #@ requires True
    #@ ensures self.v == 0
    #@ assigns self.v
    def __init__(self) -> None:
        self.v = 0

    #@ requires True
    #@ ensures self.v == k
    #@ assigns self.v
    def put(self, k: int) -> None:
        self.v = k


#@ ensures \result == 0
#@ assigns \nothing
def test_class_instances() -> int:
    """Ref 3.2.8.9: a class instance has its OWN attribute state — two instances of the
    same class are distinct objects, so writing through one leaves the other's attributes
    alone. That separation is the section's content, and it is exactly what a lowering that
    modelled instances as one shared record would get wrong. The contract pins both
    instances after only one of them is written. Previously the whole body was
    `return 0`."""
    a = Box()
    b = Box()
    a.put(5)
    if a.v == 5 and b.v == 5:
        return 0
    return 1


if __name__ == "__main__":
    assert test_class_instances() == 0
