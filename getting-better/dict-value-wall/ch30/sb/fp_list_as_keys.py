from typing import Any, Dict

PyVal = Any

#@ ensures \result == True
#@ assigns \nothing
def first_is_str(d: Dict[str, PyVal]) -> bool:
    xs = d.get("xs") or []
    for x in xs:
        return isinstance(x, str)
    return True

if __name__ == "__main__":
    print(first_is_str({"xs": [{"k": 1}]}))
