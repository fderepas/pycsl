# route #343: `not self` runs __len__ returning -1 -> ValueError
class P:
    def __len__(self) -> int:
        return -1

    #@ no_exception \all
    def m(self) -> bool:
        return not self

if __name__ == "__main__":
    P().m()
