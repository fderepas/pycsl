# Route #436 enumeration (executor g5): which str / bytes / bytearray / list / int method parameters
# CPython converts to a C Py_ssize_t / int (OverflowError past the range). Run: python3 cpython-ssize-enum.py
N = 10**20
tests = {
    "str.split": lambda: "a b".split(" ", N), "str.split kw": lambda: "a b".split(maxsplit=N),
    "str.rsplit": lambda: "a b".rsplit(" ", -N), "str.replace": lambda: "a".replace("a", "b", N),
    "str.expandtabs 2**31": lambda: "a".expandtabs(2**31), "str.expandtabs -2**31-1": lambda: "a".expandtabs(-2**31 - 1),
    "str.center": lambda: "a".center(N), "str.ljust": lambda: "a".ljust(-N), "str.rjust": lambda: "a".rjust(-N),
    "str.zfill": lambda: "a".zfill(-N), "str.find start": lambda: "a".find("a", N),
    "str.count": lambda: "a".count("a", -N, N), "str.startswith": lambda: "a".startswith("a", N),
    "str.index": lambda: "a".index("a", -N), "str.splitlines": lambda: "a".splitlines(N),
    "bytes.split": lambda: b"a b".split(b" ", N), "bytes.replace": lambda: b"a".replace(b"a", b"b", N),
    "bytes.center": lambda: b"a".center(-N), "bytes.zfill": lambda: b"a".zfill(-N),
    "bytes.expandtabs": lambda: b"a".expandtabs(2**31), "bytes.find": lambda: b"a".find(b"a", N),
    "bytes.hex": lambda: b"ab".hex(":", N), "bytearray.insert": lambda: bytearray(b"a").insert(N, 1),
    "bytearray.pop": lambda: bytearray(b"a").pop(N), "list.insert": lambda: [1].insert(N, 1),
    "list.insert neg": lambda: [1].insert(-N, 1), "list.pop": lambda: [1].pop(N),
    "list.index": lambda: [1].index(1, -N, N), "tuple.index": lambda: (1,).index(1, -N, N),
    "int.to_bytes": lambda: (1).to_bytes(N, "big"), "round float": lambda: round(1.5, N),
    "enumerate start": lambda: list(enumerate([1], N)), "sum start": lambda: sum([1], N),
    "str.split -2**63": lambda: "a b".split(" ", -2**63), "str.split 2**63": lambda: "a b".split(" ", 2**63),
    "str.split 2**63-1": lambda: "a b".split(maxsplit=2**63 - 1),
    "bytes(N)": lambda: bytes(N), "bytearray(N)": lambda: bytearray(N), "str*N": lambda: "a" * N,
}
for k, f in tests.items():
    try:
        f(); print(k, "OK")
    except Exception as e:
        print(k, type(e).__name__, e)
