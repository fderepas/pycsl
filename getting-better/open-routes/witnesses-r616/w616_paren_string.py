r"""route #616 witness: calls of body-less contracted `val`s (the str stdlib ops) whose STRING
argument contains a parenthesis. Before #616 the #267 call-site rewriter counted the `(` / `)`
inside the string literal, built an ill-formed probe body, why3 rejected it, and the probe never
ran (a non-failing warning). Honest verdict: SUCCESS. CPython: wrap("(a)") == 1, wrap("a") == 0,
close_only(")") == 2.
"""


#@ ensures \result >= 0
#@ ensures \result <= 1
#@ assigns \nothing
def wrap(s: str) -> int:
    if s.startswith("(") and s.endswith(")"):
        return 1
    return 0


#@ ensures \result >= 0
#@ assigns \nothing
def close_only(s: str) -> int:
    if s == ")":
        return 2
    return 0


if __name__ == "__main__":
    print(wrap("(a)"), wrap("a"), close_only(")"))
