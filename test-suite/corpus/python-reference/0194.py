"""Test 0194 — Python Reference 8.6.3: Irrefutable Case Blocks"""
_ = 0  # anchor
#@ ensures \result == 1
def test_match_irrefutable_case() -> int:
    """Irrefutable case: capture pattern or wildcard."""
    x = 99
    match x:
        case n:
            return 1

if __name__ == "__main__":
    assert test_match_irrefutable_case() == 1
