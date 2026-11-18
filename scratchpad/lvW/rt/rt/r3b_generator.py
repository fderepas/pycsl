from typing import Iterator, Tuple

def gen(n: int) -> Iterator[Tuple[bool, str]]:
    i = 0
    while i < n:
        if i == 2:
            yield True, ""
            return
        yield False, "n"
        i += 1
