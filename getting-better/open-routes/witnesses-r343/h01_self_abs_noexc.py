# r337: fieldless receiver is `type p = int`; builtins applied to self (not an operator)
class P:
    #@ no_exception \all
    def m(self) -> int:
        return abs(self)

if __name__ == "__main__":
    print(P().m())
