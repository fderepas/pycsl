# advice probe (route #449): witness 6953 called with exactly its parameters -- must VERIFY
def parse(path: str, mode: int) -> int:
    return len(path) + mode


#@ no_exception \all
def f(path: str, mode: int) -> int:
    return parse(path, mode)
