"""Helper for corpus 7278 (route #468): getattr(x, "append")(1)."""
from typing import List


def g(x: List[int]) -> None:
    getattr(x, "append")(1)
