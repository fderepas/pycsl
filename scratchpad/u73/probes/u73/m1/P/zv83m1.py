def _two() -> int:
    return 2


def __mro_entries__(bases):
    import hw83m1
    hw83m1.one = _two
    return ()
