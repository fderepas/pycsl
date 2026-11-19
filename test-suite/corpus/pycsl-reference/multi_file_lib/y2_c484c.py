"""Helper for corpus 7682 (routes #483 / #484 CONTROL): a class instantiated at import; instance fields only."""


class Box:
    def __init__(self, v: int) -> None:
        self.v = v
        self.tag = getattr(self, "v", 0)


DEFAULT = Box(4)
