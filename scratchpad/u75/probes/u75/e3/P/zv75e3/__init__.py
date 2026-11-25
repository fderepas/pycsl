class K:
    @staticmethod
    def one() -> int:
        return 2


def _ga(name):
    if name == "b":
        return K
    raise AttributeError(name)


def _f(x=(__getattr__ := _ga)):
    return x
