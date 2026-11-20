r"""route #613 probe n1: a program with NO import statement at all. `str.encode("idna")` makes
CPython's codec registry import `encodings.idna`, which imports `re` and `stringprep`; with the
script's directory first on sys.path, a local `re.py` is the module that `encodings.idna` gets.
(The builtins' C code imports modules pycsl cannot see: the closure is never empty.)"""


#@ ensures \result == 1
#@ assigns \nothing
def one() -> int:
    return 1


if __name__ == "__main__":
    print("encoded", "a".encode("idna"))
    print("result", one())
