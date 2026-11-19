class W:
    pass

#@ no_exception \all
def f(w: W) -> int:
    t = w
    t += 1
    return 0

if __name__ == "__main__":
    print(f(W()))
