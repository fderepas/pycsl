class K:
    @staticmethod
    def one() -> int:
        return 2


def go() -> None:
    from sys import modules as M
    x = M.get("zv81a7")
    x.b = K
