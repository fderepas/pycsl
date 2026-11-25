class K:
    @staticmethod
    def one() -> int:
        return 2


def _me(bases):
    bases[0].b = K
    return ()


def __getattr__(name):
    if name == "__mro_entries__":
        return _me
    raise AttributeError(name)
