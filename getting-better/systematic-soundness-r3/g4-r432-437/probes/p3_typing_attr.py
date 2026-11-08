import typing
#@ no_exception \all
def f(x: typing.Optional[str]) -> int:
    return len(x.strip())
