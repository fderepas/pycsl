# pycsl-flags: --memory-model hoare
"""0450 — B4 surface lock: the remaining constructs the literal `check_code`
driver uses, beyond B1/B2/B3. Body-verified, 0 \trusted; hoare model.

Three things, all of which already lower correctly — this test pins them so a
regression is caught:

  * `super().__init__()` — a subclass of an IMPORTED base (B1's
    `visitor_base.NodeVisitor`) that calls `super().__init__()` in its own
    `__init__`; the inherited init runs and the merged invariant holds at
    construction (`analyze` builds one and calls its method).

  * explicit `SyntaxError` + `try/except` — `SyntaxError` is a first-class
    *explicit* exception (raised by `\abstract` `parse`, caught by the handler)
    via the B3 raises-contract machinery. It is deliberately NOT in
    `exception_model.KNOWN_EXCEPTIONS`, which is reserved for exceptions with a
    mathematical *implicit* trigger (ZeroDivision/Index/Key/Value/StopIteration);
    `SyntaxError` has no such trigger. `except (ValueError, SyntaxError)` (the
    multi-type handler) is exercised in 0449.

  * `print` / `type` / f-strings — runtime DECORATION. They carry no proof
    obligation and no observable `assigns` effect, so a verified function that
    uses them proves exactly as if they were absent. Policy: tolerated, never
    verified (their results must not feed proven content). See the
    agent-stdlib-annotate SKILL.

*Known gap (deferred):* constructing a record instance INSIDE a `try` body
(`analyzer = FunctionAnalyzer()` between `try:` and `except`) currently
mistypes the local as `int` — the same try/nested-block local-typing family as
B3's deferred dict-from-call read-back. The literal `check_code` (C3) needs it;
tracked there. Here `analyze` builds the instance outside any `try`.
"""
import multi_file_lib.visitor_base as vb


#@ class invariant self.count >= 0
class FunctionAnalyzer(vb.NodeVisitor):
    def __init__(self):
        super().__init__()                 # base NodeVisitor.__init__ → _depth = 0
        self.count = 0

    #@ ensures \result >= 0
    #@ assigns \nothing
    def visit_FunctionDef(self, node: int) -> int:
        return 1


#@ ensures \result >= 0
#@ assigns \nothing
def analyze() -> int:
    a = FunctionAnalyzer()                 # super().__init__() ran; invariant holds
    return a.visit_FunctionDef(0)


#@ \abstract
#@ raises SyntaxError when True
def parse(src: int) -> int:
    return 0


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def safe_parse(src: int) -> int:
    try:
        parse(src)
        return 1
    except SyntaxError:
        return 0                           # unparsable input handled, total


#@ ensures \result == x
#@ assigns \nothing
def decorated(x: int) -> int:
    t = type(x)                            # decoration: result unused
    print(f"value {x} has type {t}")       # decoration: print + f-string
    return x


if __name__ == "__main__":
    print("PASS")
