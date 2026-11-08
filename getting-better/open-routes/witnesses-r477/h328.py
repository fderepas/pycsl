def __getattr__(name: str) -> int:
    d: dict[str, int] = {}
    return d[name]
