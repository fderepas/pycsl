#@ ensures \result == 1
def b() -> int:
    return 1


def __getattr__(name: str) -> object:
    import importlib
    return importlib.import_module("." + name, __name__)
