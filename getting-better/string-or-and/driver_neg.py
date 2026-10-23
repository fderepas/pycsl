"""string-valued `or`/`and` FALSE-TWIN driver — must be UNPROVEN.

`"a" or "b"` faithfully returns "a" (the first operand is non-empty), never "b".
The contract claims "b", which is FALSE of the real semantics, so it must NOT
prove. A green proof here would mean the string-ITE lowering is unsound.
"""


#@ ensures \result == "b"
def or_wrong_UNSOUND() -> str:
    """Returns "a" or "b" (== "a") but CLAIMS "b". FALSE — must not prove."""
    return "a" or "b"


if __name__ == "__main__":
    assert or_wrong_UNSOUND() == "a"
