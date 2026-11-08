from typing import Any, Optional, Union, TypeVar
T = TypeVar("T")


#@ ensures \result == 5
#@ assigns \nothing
def f(x: Union[int, Any]) -> int:
    if x is not None:
        return 6
    return 5


if __name__ == "__main__":
    print(f(1))
