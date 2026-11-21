def g(x: int) -> int:
    return x


def __getattr__(name: str) -> int:
    raise KeyError(name)
