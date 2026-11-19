"""v75 AGREE — `f"" == ""` is True, and after ROUTE #199's FAITHFUL repair the model proves it.

The AGREE half matters as much as the DISAGREE half here: #199's repair answers the empty
f-string with the empty string's own representation rather than an opaque, so the TRUE claim
is provable. A later 'simplification' to an opaque would keep v74 green and turn this red.
"""


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    s = f""
    if s == "":
        return 1
    return 2


if __name__ == "__main__":
    print(f())
