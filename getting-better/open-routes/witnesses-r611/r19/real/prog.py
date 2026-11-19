# u49 bypass? the program is a SYMLINK; CPython puts the REAL dir on sys.path[0] (it holds hashlib.pyc), pycsl uses abspath (the link dir)
# sys.path[0] (the script dir) loads it before the stdlib entry; pycsl's resolver looks only for
# `.py` / `__init__.py`, so it finds no local file, treats `hashlib` as the stdlib module and the lvV
# deterministic digest model applies.
import hashlib


#@ ensures \result == True
#@ assigns \nothing
def same(s: str) -> bool:
    return hashlib.sha256(s.encode()).hexdigest() == hashlib.sha256(s.encode()).hexdigest()


if __name__ == "__main__":
    r = same("abc")
    print("VIOLATION contract" if r is not True else "result", r)
