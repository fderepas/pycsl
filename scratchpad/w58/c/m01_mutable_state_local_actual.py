from typing import Set

#@ mutable_state
class C:
    def helper(self, s: Set[int]) -> None:
        s.add(1)

    #@ ensures \result == 0
    def caller(self) -> int:
        u: Set[int] = set()
        self.helper(u)
        return 1 if 1 in u else 0

if __name__ == "__main__":
    print(C().caller())
