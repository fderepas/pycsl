class P:
    #@ no_exception \all
    #@ ensures \result == False
    def m(self) -> bool:
        s = self
        return s < s

if __name__ == "__main__":
    print(P().m())
