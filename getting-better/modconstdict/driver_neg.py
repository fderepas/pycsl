"""module-const-dict-get FALSE-TWIN driver — must be UNPROVEN.

`OP_MAP.get("==", "==")` faithfully returns "=", never "<>". The contract claims
"<>", which is FALSE of the real mapping, so it must NOT prove. A green proof here
would mean the chained-ITE lowering is unsound.
"""
OP_MAP = {
    "==": "=",
    "!=": "<>",
    "//": "div",
    "%": "mod",
}


#@ ensures \result == "<>"
def translate_wrong_UNSOUND() -> str:
    """Returns OP_MAP.get("==", "==") (== "=") but CLAIMS "<>". FALSE — must not prove."""
    return OP_MAP.get("==", "==")


if __name__ == "__main__":
    assert translate_wrong_UNSOUND() == "="
