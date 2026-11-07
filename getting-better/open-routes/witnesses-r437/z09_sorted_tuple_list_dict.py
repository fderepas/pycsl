from typing import Dict, List, Tuple

#@ no_exception \all
def f(xs: List[Tuple[int, List[Dict[str, int]]]]) -> int:
    ys = sorted(xs)
    return len(ys)


if __name__ == "__main__":
    try:
        r = f([(1, [{"x": 1}]), (1, [{"y": 2}])])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
