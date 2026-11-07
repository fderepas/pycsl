"""Test 0873 — module-const-dict-get soundness lock (NEGATIVE twin of 0872). # pycsl-expected: FAIL

The soundness floor for the module-level constant str->str dict `.get` recognizer.
`OP_MAP.get("==", "==")` faithfully returns "=", never "<>". The contract CLAIMS
"<>", which is FALSE of the real mapping, so it must remain UNPROVEN (neither
Alt-Ergo nor Z3 discharges it). If this test ever PASSES, the chained-ITE lowering
has become unsound (a wrong-value dict read proved green — severity-1).
"""
# pycsl-expected: FAIL
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
    # OP_MAP.get("==", "==") == "=", but the contract claims "<>". FALSE.
    assert translate_wrong_UNSOUND() == "="
