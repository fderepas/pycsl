_ = 0  # anchor


#@ ensures \result == 0
def probe() -> int:
    s: str = "hello"
    return s.find("z")
