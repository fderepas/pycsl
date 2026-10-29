def __getattr__(name: str) -> int:
    raise AttributeError(name)
