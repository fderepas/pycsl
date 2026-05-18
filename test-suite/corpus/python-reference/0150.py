"""Test 0150 — Python Reference 6.3.2.4: Formal subscription grammar"""
_ = 0  # anchor
#@ ensures \result == 0
def test_formal_subscription_grammar() -> int:
    """Subscription grammar: primary[expression_list]."""
    d = {(1,2): "ok"}
    assert d[1,2] == "ok"
    return 0

if __name__ == "__main__":
    assert test_formal_subscription_grammar() == 0
