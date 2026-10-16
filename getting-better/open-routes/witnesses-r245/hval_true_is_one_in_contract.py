from typing import Any, Dict

PyVal = Any


#@ requires d["a"] == d["b"]
#@ ensures isinstance(d["a"], bool) == isinstance(d["b"], bool)
#@ assigns \nothing
def f(d: Dict[str, PyVal]) -> int:
    return 0


if __name__ == "__main__":
    dd = {"a": True, "b": 1}
    print(dd["a"] == dd["b"], isinstance(dd["a"], bool) == isinstance(dd["b"], bool))
