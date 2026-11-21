class P:
    #@ no_exception \all
    def m(self) -> int:
        return max(self, 0)

if __name__ == "__main__":
    print(P().m())
