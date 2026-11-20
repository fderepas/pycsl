# route #613 witness: a plain local dependency that imports the stdlib `json`; the `re.py` in this
# same root is then the `re` that `json` runs.
import json


#@ ensures \result == 1
#@ assigns \nothing
def one() -> int:
    return 1
