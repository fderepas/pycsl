import zv81a3

class K:
    @staticmethod
    def one() -> int:
        return 2


def _meta(name, bases, ns):
    bases[0].b = K
    return K


def swap() -> None:
    class C(zv81a3, metaclass=_meta):
        pass
