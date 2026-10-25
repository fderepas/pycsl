# route #343: "".join([self]) -> TypeError
class P:
    #@ no_exception \all
    def m(self) -> int:
        s = "".join([self])
        return 0

if __name__ == "__main__":
    P().m()
