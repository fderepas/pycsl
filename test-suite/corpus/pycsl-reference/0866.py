"""Test 0866 — WL-06d regression lock (NEGATIVE twin of 0865). # pycsl-expected: FAIL

Guards the str-LITERAL `.encode()` content law (P1-literal) from OVER-CLAIMING. For
`"abc".encode()` the byte at index 0 is `ord('a') == 97`, so the claim `\result == 98`
is FALSE and must NOT prove. If this test ever PASSES, the encode-literal fold has
collapsed the code-point content (unsound).

Prover note: pinned to Z3 (`# pycsl-flags: --prover Z3,,`). A FALSE goal over an
array-literal read makes Alt-Ergo instantiate and time out; Z3 refutes promptly.
"""
# pycsl-expected: FAIL
# pycsl-flags: --prover Z3,,
_ = 0  # anchor


#@ ensures \result == 98
def enc_false_UNSOUND() -> int:
    """char 0 of "abc" is 'a'=97, NOT 98 — must NOT prove."""
    b = "abc".encode()
    return b[0]


if __name__ == "__main__":
    assert "abc".encode()[0] == ord("a")  # 97, not 98
