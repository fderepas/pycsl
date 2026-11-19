# route #343: s = self.me() (-> "P") then s < s under no_exception (class with no __lt__)
class P:
    def me(self) -> "P":
        return self

    #@ no_exception \all
    def m(self) -> bool:
        s = self.me()
        return s < s

if __name__ == "__main__":
    P().m()
