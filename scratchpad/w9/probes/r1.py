_ = 0  # anchor
class C:
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self) -> None:
        pass

#@ requires True
#@ ensures \result == 0
def f() -> int:
    x = C()
    if x:
        return 7
    return 0
if __name__ == "__main__":
    print(f())
