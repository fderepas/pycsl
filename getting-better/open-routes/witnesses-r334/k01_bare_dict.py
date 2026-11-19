from typing import List, Dict, Sequence
#@ ensures \result == True
#@ assigns \nothing
def g(d: dict) -> bool:
    if "a" not in d:
        return True
    return d["a"] % 1 == 0

if __name__ == "__main__":
    assert g({"a": 0.5}) == True, g({"a": 0.5})
