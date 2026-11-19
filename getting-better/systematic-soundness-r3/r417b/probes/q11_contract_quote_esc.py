#@ ensures \result == "q\"q"
#@ no_exception \all
def k() -> str:
    return 'q"q'
if __name__ == "__main__":
    print(k())
