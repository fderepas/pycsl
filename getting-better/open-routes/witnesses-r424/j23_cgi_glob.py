class K:
    def __class_getitem__(cls, item: int) -> list:
        return [item]


G = K[1]


#@ no_exception \all
def f() -> int:
    s = {G}
    return len(s)


if __name__ == "__main__":
    try:
        r = f()
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
