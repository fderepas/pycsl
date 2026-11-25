import zv81a9

class K:
    @staticmethod
    def one() -> int:
        return 2


def swap() -> None:
    d = zv81a9.__getstate__()
    d["b"] = K
