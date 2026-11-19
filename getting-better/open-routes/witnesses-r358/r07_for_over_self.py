# route #343: iterating the field-less receiver -> TypeError
class P:
    #@ no_exception \all
    def m(self) -> int:
        n = 0
        for z in self:
            n = n + 1
        return n

if __name__ == "__main__":
    P().m()
