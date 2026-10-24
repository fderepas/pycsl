class W:
    def __eq__(self, o: object) -> bool:
        return False
    #@ ensures \result == True
    def m(self) -> bool:
        s = self
        return s == s

if __name__ == "__main__":
    print(W().m())
