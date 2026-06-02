#@ ensures (b != 0) ==> (\result[0] == (a // b))
#@ ensures (b != 0) ==> (\result[1] == (a % b))
#@ assigns \nothing
def divmod_pair(a: int, b: int) -> tuple:
    return (a // b, a % b)
