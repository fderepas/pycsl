from typing import Dict, List


#@ no_exception \all
def f(d: Dict[int, int], xs: List[int], c: bool) -> int:
    for x in xs:
        if c:
            for k, v in d.items():
                d.pop(k)
    return 0
