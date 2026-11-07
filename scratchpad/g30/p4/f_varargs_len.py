from typing import List


def collect(*args: int) -> List[int]:
    return sorted(args)


#@ ensures \result == 1
def probe() -> int:
    return len(collect(3, 1, 2))
