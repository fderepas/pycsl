# route #343: direct attribute read of a missing attribute on a field-less receiver
class P:
    #@ no_exception \all
    def m(self) -> int:
        y = self.zz
        return 0

if __name__ == "__main__":
    P().m()
