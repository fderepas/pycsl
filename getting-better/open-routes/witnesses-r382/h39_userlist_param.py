from collections import UserList

#@ no_exception \all
#@ ensures \result == 1
def g(d: UserList) -> int:
    s = {d}
    return 1

if __name__ == "__main__":
    print(g(UserList()))
