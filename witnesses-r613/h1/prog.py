r"""route #613 probe h1: the program imports ONLY `hashlib`; a local `_hashlib.py` sits beside it.
The stdlib `hashlib` does `import _hashlib` (the OpenSSL extension in lib-dynload, AFTER the
script directory on sys.path), so CPython loads ./_hashlib.py."""
import hashlib


#@ ensures \result == True
#@ assigns \nothing
def same(s: str) -> bool:
    return hashlib.sha256(s.encode()).hexdigest() == hashlib.sha256(s.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    print("result", same("abc"))
