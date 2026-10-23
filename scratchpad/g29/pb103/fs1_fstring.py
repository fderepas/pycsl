_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    n: int = 42
    s: str = f"v{n}"
    return len(s)
