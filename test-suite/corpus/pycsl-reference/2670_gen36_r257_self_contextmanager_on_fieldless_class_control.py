r"""Test 2670 — route #257 CONTROL (expected PASS): the shape the self-annotation mirror's
`_Unparser` uses 41 times — `with self.delimit():` inside a method, where `delimit` is an
in-file `@contextmanager` method that only calls `self` methods, on a class whose model
record has NO FIELDS. Every effect the generator can have lands in a record the model does
not have, so erasing the header loses nothing the model could state; the `with` body is
still emitted and the TRUE contract proves.
"""
from contextlib import contextmanager
from typing import Iterator


class W:
    #@ \trusted reviewer: route257-control
    #@ ensures \result == 0
    #@ assigns \nothing
    def emit(self) -> int:
        return 0

    #@ ensures \result == 0
    #@ assigns \nothing
    def zero(self) -> int:
        return 0

    #@ assigns \nothing
    @contextmanager
    def delimit(self) -> Iterator[int]:
        self.emit()
        yield 0
        self.emit()

    #@ ensures \result == 9
    #@ assigns \nothing
    def run(self) -> int:
        x = self.zero()
        with self.delimit():
            x = x + 9
        return x


if __name__ == "__main__":
    assert W().run() == 9
