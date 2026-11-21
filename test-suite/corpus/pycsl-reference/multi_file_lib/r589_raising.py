from typing import List


class E589(Exception):
    pass


#@ raises E589 when True
def g589(xs: List[int]) -> int:
    raise E589("a", xs[9])
