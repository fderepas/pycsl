class C:
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def push(self, a: list) -> None:
        a.append(1)

#@ requires \length(a) == 2
#@ ensures \result == 2
#@ assigns \nothing
def f(a: list) -> int:
    c = C()
    c.push(a)
    return len(a)
