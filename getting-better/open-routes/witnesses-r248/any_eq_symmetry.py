from typing import Any


#@ requires x == y
#@ ensures y == x
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    return 0


class A:
    def __eq__(self, o: object) -> bool:
        return True


class B:
    def __eq__(self, o: object) -> bool:
        return False


if __name__ == "__main__":
    print(A() == B(), B() == A())
