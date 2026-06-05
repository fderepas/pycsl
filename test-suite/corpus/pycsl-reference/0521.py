"""Test 0521 — sum types: payload constructors, construction + capture match.

A `#@ datatype` constructor may carry typed payloads (`Some(int)`, `Rect(int, int)`). An applied
constructor `o = Some(7)` lowers to a typed variant local `let o = ref (Some 7) in` (not a clashing
int `ref 0`), and a `case Some(v):` arm binds the payload (`| Some v -> ...`) so a postcondition
relating the result to the captured field discharges. Mixed nullary + multi-arg constructors share
one exhaustive `match`."""
#@ datatype Box = Some(int) | Pair(int, int) | Empty
_ = 0  # anchor


#@ ensures \result == 7
def build_and_read() -> int:
    o = Some(7)
    match o:
        case Some(v):
            return v
        case Pair(a, b):
            return a + b
        case Empty():
            return 0


#@ ensures \result == 0 or \result == 1 or \result == 2
def tag(b: Box) -> int:
    match b:
        case Some(v):
            return 0
        case Pair(x, y):
            return 1
        case Empty():
            return 2
