class K:
    @staticmethod
    def one() -> int:
        return 2


def __mro_entries__(bases):
    setattr(bases[0], "b", K)
    return ()
