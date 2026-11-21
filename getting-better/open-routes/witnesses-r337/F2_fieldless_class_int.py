# F2: a fieldless user class is `type w = int`: its values get int laws (user dunders / TypeError ignored)
class W:
    def __sub__(self, o: object) -> int:
        return 1

class P:
    pass

#@ ensures \result == 0
def f_dunder_sub(x: W) -> int:
    return x - x

#@ no_exception \all
#@ ensures \result == False
def f_lt_noexc(x: P) -> bool:
    return x < x

#@ no_exception \all
#@ ensures \result == 1
def f_mul_noexc(x: P) -> int:
    return x * 0 + 1

if __name__ == "__main__":
    import rt23h
    rt23h.check([
        ("f_dunder_sub", f_dunder_sub, (W(),), 0),
        ("f_lt_noexc", f_lt_noexc, (P(),), False),
        ("f_mul_noexc", f_mul_noexc, (P(),), 1),
    ])
