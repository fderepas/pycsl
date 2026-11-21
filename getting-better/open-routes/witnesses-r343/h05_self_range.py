class P:
    #@ no_exception \all
    #@ ensures \result == 0
    def m(self) -> int:
        r = range(self)
        return 0

if __name__ == "__main__":
    print(P().m())
