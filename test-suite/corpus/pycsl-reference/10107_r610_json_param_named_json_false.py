r"""Test 10107 -- route #610 (rt61 M1, expected FAIL): a PARAMETER named `json`: `json.dumps(..)` is the user method (an effect on `json.n`). The model of the module call
applies only when the head name is the module import, bound nowhere in the function and not
rebound at module level; here it is not, so the file is REFUSED
(`PYCSL-R610-EXT-MODULE-NAME-SHADOWED`) rather than lowered as the module call.
"""
# pycsl-expected: FAIL
import json


class J:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    def dumps(self, x: int) -> str:
        self.n = self.n + 1
        return ""


#@ ensures \result == 0
def f(json: J) -> int:
    b = json.n
    try:
        json.dumps(b)
    except ValueError:
        return 0
    except TypeError:
        return 0
    except RecursionError:
        return 0
    return json.n - b


if __name__ == "__main__":
    r = f(J())
    print("VIOLATION contract" if r != 0 else "result", r)
