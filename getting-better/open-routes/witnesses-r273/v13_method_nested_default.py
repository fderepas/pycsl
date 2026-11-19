# FALSE: nested def default inside a method mutates self.v.
class C:
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures \result == 1
    #@ assigns self.v
    def push(self) -> int:
        self.v = 5
        return 1

    #@ requires self.v == 0
    #@ ensures \result == 0
    #@ assigns self.v
    def f(self) -> int:
        def inner(y: int = self.push()) -> int:
            return y
        return self.v

if __name__ == "__main__":
    print(C().f())
