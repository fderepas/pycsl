_ = 0  # anchor


#@ ensures \result == 1
def probe() -> int:
    s: str = "  ab  "
    t: str = s.strip()
    if t == "  ab  ":
        return 1
    return 0
