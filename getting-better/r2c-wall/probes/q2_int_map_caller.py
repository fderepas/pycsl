from typing import Dict

#@ assigns d
def setk(d: Dict[str, int]) -> None:
    d["k"] = 5

#@ ensures \result == 5
#@ assigns \nothing
def caller() -> int:
    d: Dict[str, int] = {"k": 1}
    setk(d)
    return d["k"]
