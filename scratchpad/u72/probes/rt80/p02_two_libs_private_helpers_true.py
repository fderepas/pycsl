import rt80_priv_a
import rt80_priv_b


#@ ensures \result == 3
#@ assigns \nothing
def g() -> int:
    return rt80_priv_a.x() + rt80_priv_b.y()

if __name__ == "__main__":
    print(g())
