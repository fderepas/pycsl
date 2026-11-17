# R610 / route #326 bypass? a SOURCELESS `hashlib.pyc` beside the program: CPython's FileFinder for
# sys.path[0] (the script dir) loads it before the stdlib entry; pycsl's resolver looks only for
# `.py` / `__init__.py`, so it finds no local file, treats `hashlib` as the stdlib module and the lvV
# deterministic digest model applies.
# needs: hashlib.pyc
import hashlib


#@ ensures \result == True
#@ assigns \nothing
def same(s: str) -> bool:
    return hashlib.sha256(s.encode()).hexdigest() == hashlib.sha256(s.encode()).hexdigest()


if __name__ == "__main__":
    r = same("abc")
    print("VIOLATION contract" if r is not True else "result", r)
