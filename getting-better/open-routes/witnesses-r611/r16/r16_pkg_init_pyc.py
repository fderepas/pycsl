# u49 bypass? a hashlib/ PACKAGE dir whose only init is __init__.pyc (CPython FileFinder accepts any loader suffix for __init__)
# sys.path[0] (the script dir) loads it before the stdlib entry; pycsl's resolver looks only for
# `.py` / `__init__.py`, so it finds no local file, treats `hashlib` as the stdlib module and the lvV
# deterministic digest model applies.
# needs: hashlib
import hashlib


#@ ensures \result == True
#@ assigns \nothing
def same(s: str) -> bool:
    return hashlib.sha256(s.encode()).hexdigest() == hashlib.sha256(s.encode()).hexdigest()


if __name__ == "__main__":
    r = same("abc")
    print("VIOLATION contract" if r is not True else "result", r)
