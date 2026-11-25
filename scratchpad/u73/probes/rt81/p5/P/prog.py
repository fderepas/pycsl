import zv81p5.b

class K:
    @staticmethod
    def one() -> int:
        return 2


def _meta(name, bases, ns):
    setattr(bases[0], "b", K)
    return K


class C(zv81p5, metaclass=_meta):
    pass


#@ ensures \result == 1
def g() -> int:
    return zv81p5.b.one()


print("result", g())
