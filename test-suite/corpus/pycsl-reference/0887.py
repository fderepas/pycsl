"""Test 0887 — faithful character-level string iteration `for i, ch in enumerate(s)` (POSITIVE).

Exercises Wall-2 char iteration: `enumerate(s)` over a string lowers to an integer-indexed
`while` whose counter runs `0 .. String.length s`, binding BOTH the index `i` and the 1-char
string `ch = str_sub_op s !i 1`. A character IS a 1-char `str_sub_op` string — NO char type,
NO `seq char`, NO new theory. The guard `ch == "("` / `ch == ")"` routes through `str_eq_op`
as an UNCONSTRAINED boolean (it only selects a branch — "mechanism C" — so the SMT string
theory is never exercised). Termination is the ARITHMETIC variant `String.length s - !i`
(SMT-trivial integer subtraction; no structural measure). The slice `s[1:-1]` uses the TOTAL
`str_sub_op` (no bounds VC), `len(s)` is `String.length s`.

Faithful under-approximation: the char content is unmodelled beyond being a length-1 string;
only the type + frame + termination matter for the type-safety + frame contract. If this
regresses, the `enumerate(<str>)` recognizer, the tuple-target binding (`i`/`ch`), the char
string-typing (so `ch == "("` picks `str_eq_op`), or the arithmetic loop variant broke.
Non-@mutable_state standalone path — byte-identical corpus (no corpus program iterates chars).
"""


#@ requires True
#@ ensures True
#@ assigns \nothing
def first_balanced_prefix(s: str) -> str:
    s = s.strip()
    if not (s.startswith("(") and s.endswith(")")):
        return s
    depth = 0
    for i, ch in enumerate(s):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                return s[1:-1].strip() if i == len(s) - 1 else s
    return s
