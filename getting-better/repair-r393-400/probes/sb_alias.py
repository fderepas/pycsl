import builtins as bi
#@ ensures \result == 3
def f() -> int:
    return bi.sum([1, 2], **{"start": 10})

if __name__ == "__main__":
    print("result", f())
