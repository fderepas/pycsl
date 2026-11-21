"""v59 AGREE — an OMITTED slice upper bound is the string's own LENGTH: `'abcde'[1:]` is 'bcde', length 4. Route #190: the omitted bound arrived as a `None` node that lowered to the integer 0, so the model read the slice as `substring s 1 (0 - 1)` — a negative length, which Why3 answers with the EMPTY string."""


#@ ensures \result == 4
#@ assigns \nothing
def f() -> int:
    s: str = "abcde"
    return len(s[1:])


if __name__ == "__main__":
    print(f())
