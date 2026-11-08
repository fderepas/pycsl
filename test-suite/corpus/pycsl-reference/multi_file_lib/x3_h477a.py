"""Helper for corpus 7470 / 7473 (route #477): a module `__getattr__` that raises KeyError."""


def __getattr__(name: str) -> int:
    d: dict[str, int] = {}
    return d[name]
