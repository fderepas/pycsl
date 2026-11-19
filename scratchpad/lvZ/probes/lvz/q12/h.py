from pathlib import Path


class Box:
    def __init__(self, n: int) -> None:
        self.n = n

    def mk(self, s: str) -> Path:
        return Path(s)
