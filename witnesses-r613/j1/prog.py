r"""route #613 probe j1: the program imports ONLY `json`; a local `re.py` sits beside it.
CPython puts the script's realpath directory first on sys.path, so the stdlib `json`'s own
`import re` (json/decoder.py, encoder.py, scanner.py) loads ./re.py."""
import json


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    s = json.dumps("a")
    return 1


if __name__ == "__main__":
    print("result", f())
