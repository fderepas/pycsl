def has_ga(x: object) -> bool:
    return hasattr(x, "__getattr__")


#@ ensures \result == 3
def three() -> int:
    return 3
