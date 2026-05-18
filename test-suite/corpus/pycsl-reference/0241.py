"""Test 0241 — PyCSL Annotation Reference 7.4 (match with assignment)"""
# pycsl-flags: --no-proof
_ = 0  # anchor
#@ requires code >= 0
#@ ensures \result >= 0
def test_match_assign(code: int) -> int:
    result = 0
    match code:
        case 200:
            result = 1
        case 404:
            result = 2
        case _:
            result = 0
    return result

if __name__ == "__main__":
    assert test_match_assign(200) == 1
    assert test_match_assign(404) == 2
    assert test_match_assign(500) == 0
