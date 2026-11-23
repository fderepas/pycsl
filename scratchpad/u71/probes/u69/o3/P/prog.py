import zu697


def load() -> None:
    import zu697.b


#@ ensures \result == 1
def g() -> int:
    return zu697.b()


load()
print("result", g())
