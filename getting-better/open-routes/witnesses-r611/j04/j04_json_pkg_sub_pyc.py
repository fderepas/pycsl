# u49 bypass? json/ = the stdlib json package (every .py byte-identical) with encoder.py REMOVED and a sourceless evil encoder.pyc
# needs: json
import json


class Q:
    #@ assigns \nothing
    def __init__(self) -> None:
        self.n: int = 0


#@ ensures \result == 0
def f(q: Q) -> int:
    b = q.n
    s = json.dumps(q)
    return q.n - b


if __name__ == "__main__":
    r = f(Q())
    print("VIOLATION contract" if r != 0 else "result", r)
