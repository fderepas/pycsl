# route #616 witness: a call of a body-less contracted `val` (the str stdlib ops) whose STRING
# argument contains a parenthesis. Before #616 the #267 call-site rewriter counted the `(` / `)`
# inside the string literal, built an ill-formed probe body, why3 rejected it, and the probe never
# ran (a non-failing warning). Honest verdict: SUCCESS (CPython: wrap("(a)") == 1, wrap("a") == 0).


def wrap(s: str) -> int:
    #@ ensures \result >= 0
    #@ ensures \result <= 1
    if s.startswith("(") and s.endswith(")"):
        return 1
    return 0


def close_only(s: str) -> int:
    #@ ensures \result >= 0
    if s == ")":
        return 2
    return 0
