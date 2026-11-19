# fieldless receiver returned through `-> int` (receiver is `type p = int`), then used as int by a verified sibling
class P:
    def m(self) -> int:
        return self

    #@ no_exception \all
    def k(self) -> int:
        return self.m() + 1

if __name__ == "__main__":
    print(P().k())
