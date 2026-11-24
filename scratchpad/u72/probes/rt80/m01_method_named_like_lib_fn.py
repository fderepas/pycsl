import rt80_liba


class K:
    def __init__(self) -> None:
        self.v = 0

    #@ ensures \result == 2
    #@ assigns \nothing
    def helper(self) -> int:
        return 2


#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    return K().helper() + rt80_liba.helper()

if __name__ == "__main__":
    print(g())
