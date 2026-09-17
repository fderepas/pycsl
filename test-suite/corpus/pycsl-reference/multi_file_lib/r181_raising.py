class C:
    def __init__(self, v: int) -> None:
        if v < 0:
            raise ValueError()
        self.v = v


class MyErr(ValueError):
    pass


def boom() -> int:
    raise MyErr()
