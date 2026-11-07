from typing import Dict
class KeyError(Exception):
    pass

#@ no_exception \all
#@ ensures \result == 1
def g(d: Dict[int, int]) -> int:
    try:
        y = d[5]
    except KeyError:
        return 1
    return 1

if __name__ == "__main__":
    assert g({}) == 1
