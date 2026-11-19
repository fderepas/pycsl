# FALSE: ord(chr(300)) == 300, claim != 300.
#@ ensures \result != 300
#@ assigns \nothing
def f() -> int:
    return ord(chr(300))

if __name__ == "__main__":
    print(f())
