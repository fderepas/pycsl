# route #611: a sourceless `json.pyc` beside the program shadows the stdlib json for CPython
# (FileFinder, sys.path[0]); lvQ's json.dumps model must not be taken.
# needs: json.pyc (compiled from w3src/json.py: dumps returns "X")
import json


#@ ensures \result == True
#@ assigns \nothing
def same() -> bool:
    return json.dumps(1) == json.dumps(1)


if __name__ == "__main__":
    r = same()
    print("result", r)
