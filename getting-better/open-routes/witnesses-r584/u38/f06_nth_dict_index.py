import ast
from types import SimpleNamespace as NS

def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if x.get("type") == "Nth":
            i = x.get("index", {})
            if i.get("type") == "Var":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f({"type": "Nth", "list": {"type": "Var", "name": "a"}, "index": {"type": "Var", "name": "a"}})
    print("VIOLATION contract" if r != 0 else "result", r)
