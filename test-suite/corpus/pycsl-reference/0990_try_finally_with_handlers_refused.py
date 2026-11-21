"""Test 0990 — a `try ... except ... finally:` is REFUSED. The `finally` block was DROPPED
whenever handlers were present, and that residue is the `TRYFINAL = 9` ratchet
`bin/check-dropped-mutation.py` has been reporting green for two relaunches.

Module 6's `_handle_try_stmt` reads `stmt.body` and `stmt.handlers` and neither `finalbody`
nor `orelse`. #33 emits the `finally` in the ONE case it could — no handlers, and no jump
out of the lowered body. Everything else was counted and left. Measured, before this
refusal:

    #@ ensures \result == 2                    <-- FALSE OF THE PROGRAM
    def f() -> int:
        x: int = 1
        try:
            x = 2
        except ValueError:
            x = 9
        finally:
            x = 3
        return x

    [+] Verification SUCCESS! All contracts formally proven.

Real Python returns 3.

THE CONTROLS LOCALISE IT, which is what makes this a defect rather than a known limitation:
the SAME file with the handler removed correctly FAILS — that is #33's fixed case working —
and the `try/except/else` form correctly FAILS too. So the live gap is exactly `finally`
PLUS handlers.

Refused in Module 6's statement lowering, so a `\trusted` / `\abstract` function — whose
body is never lowered — stays exempt. CENSUS: 4 sites in the whole tree, and the one in the
mirror (`pycsl._run_proofs`) is `\trusted`, so both corpora are BYTE-IDENTICAL across this
refusal and no mirror emission moves.

A `try ... finally:` with NO handlers IS modelled. Split the statement, or move the cleanup
after the `try`.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL


#@ requires True
#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    x: int = 1
    try:
        x = 2
    except ValueError:
        x = 9
    finally:
        x = 3
    return x
