#@ ensures \result == 1
def b() -> int:
    return 1


if True:
    from .alt import b
