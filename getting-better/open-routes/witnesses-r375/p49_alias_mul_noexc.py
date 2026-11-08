class W:
    #@ no_exception \all
    def m(self) -> int:
        t = self
        t *= 2
        return 0

if __name__ == "__main__":
    print(W().m())
