"""module-const-dict-get POSITIVE driver.

A module-level constant str->str dict `OP_MAP` read via `OP_MAP.get(k, default)`
lowers to a faithful chained string if-then-else. A matched key returns its mapped
value (hit); an absent key returns the caller's default. Both discharge.
"""
OP_MAP = {
    "==": "=",
    "!=": "<>",
    "//": "div",
    "%": "mod",
}


#@ ensures \result == "="
def translate_hit() -> str:
    """OP_MAP.get("==", "==") == "=" — a matched key returns its mapped value."""
    return OP_MAP.get("==", "==")


#@ ensures \result == "<>"
def translate_hit2() -> str:
    """OP_MAP.get("!=", "!=") == "<>" — second-arm hit."""
    return OP_MAP.get("!=", "!=")


#@ ensures \result == "zzz"
def translate_default() -> str:
    """OP_MAP.get("zzz", "zzz") == "zzz" — an absent key returns the default."""
    return OP_MAP.get("zzz", "zzz")


if __name__ == "__main__":
    assert translate_hit() == "="
    assert translate_hit2() == "<>"
    assert translate_default() == "zzz"
