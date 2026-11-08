"""v69 AGREE — indexing `bytes` yields the BYTE VALUE, not a 1-byte object and not 0: `b'abc'[0]` is 97."""


#@ ensures \result == 97
#@ assigns \nothing
def f() -> int:
    b: bytes = b"abc"
    return b[0]


if __name__ == "__main__":
    print(f())
