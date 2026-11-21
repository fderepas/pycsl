class C:
    R = 0.5
    #@ ensures \result == 1
    #@ assigns \nothing
    def g(self) -> int:
        if self.R % 1 == 0:
            return 1
        return 0

if __name__ == "__main__":
    assert C().g() == 1
