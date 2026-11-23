class K:
    @staticmethod
    def one() -> int:
        return 2


def __getattr__(name):
    if name == "b":
        return K
    raise AttributeError(name)
