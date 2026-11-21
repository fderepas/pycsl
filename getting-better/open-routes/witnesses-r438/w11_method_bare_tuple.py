class C:
    #@ no_exception \all
    def m(self, t: tuple) -> int:
        s = {t}
        return len(s)


if __name__ == "__main__":
    try:
        r = C().m(([1],))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
