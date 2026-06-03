# pycsl-flags: --memory-model hoare
"""0451 — a record (and a dict) constructed INSIDE a `try` body now type-checks.
Body-verified, 0 \trusted; hoare model.

`_handle_try_stmt` used to pre-declare every try-assigned local as `let v = ref 0
in` (int), so a record/dict local built inside the `try` mistyped (record assigned
to an int ref). Now each try-local is typed from its first assignment: a record is
let-bound in the body (no outer ref), a dict gets an empty-map ref, ints keep
`ref 0`. This is the shape the literal `check_code` (C3) uses —
`analyzer = FunctionAnalyzer()` between `try:` and `except` — and the groundwork
for the B3 dict read-back.

`safe_check` mirrors `check_code`: build the analyzer inside the `try`, call its
(inherited-base + own) method, return 0/1; `except SyntaxError` makes it total.
`dict_in_try` builds an empty dict inside the `try`.
"""
import multi_file_lib.visitor_base as vb


#@ class invariant self.count >= 0
class FunctionAnalyzer(vb.NodeVisitor):
    def __init__(self):
        super().__init__()
        self.count = 0

    #@ ensures \result >= 0
    #@ assigns \nothing
    def visit_FunctionDef(self, node: int) -> int:
        return 1


#@ \abstract
#@ raises SyntaxError when True
def parse(src: int) -> int:
    return 0


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def safe_check(src: int) -> int:
    try:
        parse(src)
        analyzer = FunctionAnalyzer()                 # record built INSIDE try
        return 1 if analyzer.visit_FunctionDef(0) >= 0 else 0
    except SyntaxError:
        return 0


#@ ensures \result >= 0
#@ assigns \nothing
def dict_in_try(k: int) -> int:
    try:
        d = {}                                        # dict built INSIDE try
        return 0
    except KeyError:
        return 0


if __name__ == "__main__":
    print("PASS")
