"""Test 0091 — Python Reference 3.3.7: Emulating container types"""
_ = 0  # anchor
#@ ensures \result == 10
def test_emulating_container_types() -> int:
    """__len__, __getitem__, __setitem__, __delitem__, __contains__."""
    class Vec:
        def __init__(self, data):
            self._d = list(data)
        def __len__(self):
            return len(self._d)
        def __getitem__(self, i):
            return self._d[i]
    v = Vec([10, 20, 30])
    return v[0]

if __name__ == "__main__":
    assert test_emulating_container_types() == 10
