# route #343: type(self)() where __init__ needs an argument -> TypeError
class W:
    def __init__(self, k: int) -> None:
        pass

    #@ no_exception \all
    def m(self) -> int:
        t = type(self)()
        return 0

if __name__ == "__main__":
    W(1).m()
