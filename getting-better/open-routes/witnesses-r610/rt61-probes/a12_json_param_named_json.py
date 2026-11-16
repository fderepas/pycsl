# lvQ (pre-existing?) json.dumps: a PARAMETER named `json` shadows the module.
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
