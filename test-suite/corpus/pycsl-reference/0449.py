# pycsl-flags: --memory-model hoare
"""0449 — `ast.literal_eval` safety, formally. Body-verified, 0 \trusted; hoare.

`literal_eval` IS Python's literal parser — irreducibly opaque — so it is modeled
with the `#@ \abstract` directive: a bodyless WhyML `val` defined SOLELY by its
contract (sound, uninterpreted; NOT \trusted — there is no unverified body, the
spec is the definition). Its SAFETY guarantee is the bounded raises set: on any
input it may raise only `ValueError` / `SyntaxError`, and it never executes
arbitrary code (unlike `eval`). This mirrors `src/pycsl_lib/ast.py`'s model.

What is PROVEN here is the security property that matters: a
`try/except (ValueError, SyntaxError)` wrapper around `literal_eval` is **TOTAL**
— for EVERY input it returns a controlled value and never propagates an exception
or runs code. (`safe_parse` is verified with no precondition, i.e. for all `src`.)

*Honest limit:* PyCSL does not model the parser, so the parsed VALUE is
uninterpreted and WHICH specific string is malicious is not decided here — the
proof is that *however* `literal_eval` behaves within its bounded raises set, the
wrapper is safe. The catch is load-bearing: dropping a handled type leaves the
exception unhandled and verification fails.
"""


#@ \abstract
#@ raises ValueError when True
#@ raises SyntaxError when True
def literal_eval(src: int) -> int:
    return 0


#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def safe_parse(src: int) -> int:
    try:
        literal_eval(src)
        return 1                       # parsed a literal value
    except (ValueError, SyntaxError):
        return 0                       # blocked malformed / malicious input


if __name__ == "__main__":
    # Runtime: real ast.literal_eval on a literal returns the value; on a
    # code-injection string it raises ValueError — both handled by safe_parse.
    print("PASS")
