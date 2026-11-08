from typing import List

class W:
    pass

    #@ no_exception \all
    def m(self) -> int:
        t = self
        t += 1
        return 0

if __name__ == "__main__":
    print(W().m())
