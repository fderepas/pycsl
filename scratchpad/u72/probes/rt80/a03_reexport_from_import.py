from rt80_reex import f


#@ ensures \result == 7
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    print(g())
