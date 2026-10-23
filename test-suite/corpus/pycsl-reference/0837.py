"""Test 0837 — WL-06b regression lock (NEGATIVE twin of 0835). # pycsl-expected: FAIL

Guards the faithful byte-content model (WL-06b) from OVER-CLAIMING. `false_content`
returns `b"a"[0]`, whose faithful value is `97` (ord 'a'), but its contract falsely
claims `\\result == 98`. With the concrete literal content model, `b[0]` denotes exactly
`97`, so the claim `97 == 98` is FALSE and must NOT prove (Z3 returns Unknown). If this
test ever PASSES, the byte value has been mis-modelled (a regression to the pre-WL-06b
opaque residual, or an unsound content model).

Prover note: pinned to Z3 (`# pycsl-flags: --prover Z3,,`). A FALSE goal sitting over a
constructed `array int` literal makes Alt-Ergo's array E-matching churn to its per-goal
timeout instead of returning Unknown promptly; Z3 refutes it in milliseconds. The lock's
meaning is unchanged — a sound solver confirms the false byte value is NOT provable, and
any regression that made it provable would flip this to a Valid/PASS.
"""
# pycsl-expected: FAIL
# pycsl-flags: --prover Z3,,
_ = 0  # anchor


#@ ensures \result == 98
def false_content() -> int:
    """Returns byte 0 (= 97) but claims 98 — false under faithful content."""
    b = b"a"
    return b[0]


if __name__ == "__main__":
    # b"a"[0] == 97, NOT 98 — the contract is a deliberate falsehood.
    assert false_content() == ord("a")
