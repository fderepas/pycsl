"""Test 0174 — Python Reference 7.6: The return statement"""
_ = 0  # anchor
#@ ensures \result == 5
#@ assigns \nothing
def test_return_statement() -> int:
    """Ref 7.6: `return` leaves the enclosing function IMMEDIATELY — the statements after
    the `return` that is reached do not execute, so the value seen by the caller is the
    one at that first `return` and NOT whatever a later statement would have computed.
    Previously the whole body was `return 5`, so the postcondition was discharged by the
    tail return alone and said nothing about early exit."""
    n = 0
    if n == 0:
        return 5
    n = 99
    return n

if __name__ == "__main__":
    assert test_return_statement() == 5
