from typing import List
#@ ensures \result == 2
def f() -> int:
    parts: List[str] = ["a", "b"]
    return len("-".join(parts))
if __name__ == "__main__":
    print(f())
