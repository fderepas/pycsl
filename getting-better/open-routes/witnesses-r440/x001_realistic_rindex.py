from typing import Any, Dict, List, Optional, Set, Tuple, Union

class Buffer:
    def __init__(self) -> None:
        self.items: List[int] = []

    def rindex(self, v: int) -> int:
        return 0


#@ no_exception \all
def last_dot(path: str) -> int:
    return path.rindex(".")


if __name__ == "__main__":
    try:
        r = last_dot("README")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
