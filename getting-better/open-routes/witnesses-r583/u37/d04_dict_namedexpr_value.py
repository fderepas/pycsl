def mutable_state(cls): return cls

@mutable_state
class Em:
    #@ ensures \result == 0
    #@ assigns \nothing
    def f(self, x: "ExprIR") -> int:
        if x.get("type") == "NamedExpr":
            v = x.get("value", {})
            if v.get("type") == "Var":
                return 1
        return 0


if __name__ == "__main__":
    r = Em().f({"type": "NamedExpr", "target": "y", "value": {"type": "Var", "name": "a"}})
    print("VIOLATION contract" if r != 0 else "result", r)
