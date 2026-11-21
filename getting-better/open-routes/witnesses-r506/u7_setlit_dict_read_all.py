from typing import Dict

#@ no_exception \all
#@ ensures \result == 1
def g(m: Dict[int, int]) -> int:
    v = {m[5]}
    return 1

if __name__ == "__main__":
    print(g({}))
