#@ proof rocq: divmod_pair_fst
#@ proof rocq: divmod_pair_snd
#@ proof lean: divmod_pair_fst
#@ proof lean: divmod_pair_snd
#@ ensures (b != 0) ==> (\result[0] == (a // b))
#@ ensures (b != 0) ==> (\result[1] == (a % b))
#@ assigns \nothing
def divmod_pair(a: int, b: int) -> tuple:
    return (a // b, a % b)
