from typing import List, Dict
#@ requires 0 in d
#@ ensures \result == \old(len(d[0]))
#@ assigns d
def f(d: Dict[int, List[int]]) -> int:
    d[0].append(1)
    return len(d[0])

if __name__ == "__main__":
    x = {0: []}; print(f(x)); assert f({0: []}) == 0
