from dataclasses import dataclass

def mutable_state(cls):
    return cls

@mutable_state
@dataclass
class C:
    n: int = 0

    #@ assigns \nothing
    def bump(self) -> None:
        self.n = 9

    #@ assigns self.n
    #@ ensures \result == 1
    def get(self) -> int:
        self.n = 1
        self.bump()
        return self.n
