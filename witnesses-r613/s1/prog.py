r"""route #613 probe j0: the program imports ONLY `json` and NOTHING sits beside it (control).
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
