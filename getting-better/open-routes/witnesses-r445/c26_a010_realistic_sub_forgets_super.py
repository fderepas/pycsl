from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence
from dataclasses import dataclass

class Connection:
    def __init__(self) -> None:
        self.retries = 3


class TlsConnection(Connection):
    def __init__(self, port: int) -> None:
        self.port = port

    def budget(self) -> int:
        return self.retries * 2



#@ no_exception \all
def f(n: int) -> int:
    return TlsConnection(n).budget()


if __name__ == "__main__":
    try:
        r = f(0)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
