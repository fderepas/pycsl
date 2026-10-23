#@ ensures \result == 1
def f() -> int:
    x: int = 1
    try:
        x = 2
    except* ValueError:
        x = 3
    return x
