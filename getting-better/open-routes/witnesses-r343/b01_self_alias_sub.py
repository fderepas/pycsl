# r337 residual: s = self alias not followed by the self-operator refusal
class W:
    def __sub__(self, o: object) -> int:
        return 1
    #@ ensures \result == 0
    def m(self) -> int:
        s = self
        return s - s

if __name__ == "__main__":
    print(W().m())
