# route #343: truth test of the receiver runs __len__ (returns -1 -> ValueError)
class P:
    def __len__(self) -> int:
        return -1

    #@ no_exception \all
    def m(self) -> int:
        if self:
            return 1
        return 0

if __name__ == "__main__":
    P().m()
