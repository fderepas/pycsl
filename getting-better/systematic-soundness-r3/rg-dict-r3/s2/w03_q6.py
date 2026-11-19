from typing import Any, Dict, List

#@ no_exception \all
#@ ensures \result == 1
def names(funcs: List[Dict[str, Any]]) -> int:
    seen = set()
    for f in funcs:
        seen.add(f.get("name"))
    return 1

if __name__ == "__main__":
    print(names([{"name": ["x"]}]))
