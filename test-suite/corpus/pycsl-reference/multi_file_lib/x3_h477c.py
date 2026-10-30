"""Helper for corpus 7472 (route #477): a real `def g` next to a raising `__getattr__`."""


def g(x: int) -> int:
    return x


def __getattr__(name: str) -> int:
    raise KeyError(name)
