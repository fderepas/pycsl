class W:
    #@ no_exception \all
    def m(self) -> int:
        s = {*self}
        return 0

if __name__ == "__main__":
    print(W().m())
