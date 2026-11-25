import zv81a13

class K:
    @staticmethod
    def one() -> int:
        return 2


def swap() -> None:
    import builtins
    s = getattr(builtins, "setattr")
    s(zv81a13, "b", K)
