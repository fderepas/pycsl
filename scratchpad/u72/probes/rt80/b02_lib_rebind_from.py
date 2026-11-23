from rt80_rebind import f


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return f()

if __name__ == "__main__":
    print(g())
