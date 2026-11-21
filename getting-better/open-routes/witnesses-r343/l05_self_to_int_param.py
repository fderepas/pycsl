# fieldless receiver (`type p = int`) passed as an `int` argument
#@ no_exception \all
def h(n: int) -> int:
    return n + 1

class P:
    #@ no_exception \all
    def m(self) -> int:
        return h(self)

if __name__ == "__main__":
    print(P().m())
