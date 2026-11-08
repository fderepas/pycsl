# route #343: missing attribute read on a field-less receiver returns an int with int laws?
class W:
    #@ no_exception \all
    #@ ensures \result == 0
    def m(self) -> int:
        y = self.zz
        return y - y

if __name__ == "__main__":
    print(W().m())
