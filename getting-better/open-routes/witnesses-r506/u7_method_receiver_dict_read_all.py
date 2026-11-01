from typing import Dict, List

#@ no_exception \all
def f(xs: List[str], d: Dict[str, str]) -> int:
    return len(d["b"].upper())

if __name__ == "__main__":
    print(f([], {}))
