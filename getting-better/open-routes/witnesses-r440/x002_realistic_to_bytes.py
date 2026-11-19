from typing import Any, Dict, List, Optional, Set, Tuple, Union

class Codec:
    def to_bytes(self, n: int, width: int) -> int:
        return 0


#@ no_exception \all
def encode_byte(n: int) -> int:
    return len(n.to_bytes(1, "big"))


if __name__ == "__main__":
    try:
        r = encode_byte(256)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
