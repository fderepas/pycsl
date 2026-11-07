"""Helper for corpus 7471 (route #477): a module `__getattr__` raising AttributeError."""


def __getattr__(name: str) -> int:
    raise AttributeError(name)
