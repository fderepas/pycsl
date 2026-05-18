"""Test 0188 — PyCSL Annotation Reference 3.1.14: String literal in ensures"""
_ = 0  # anchor
#@ ensures \result == "hello"
def greet() -> str:
    """Returns a greeting string."""
    return "hello"

if __name__ == "__main__":
    assert greet() == "hello"
