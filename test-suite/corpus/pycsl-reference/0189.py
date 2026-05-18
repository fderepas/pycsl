"""Test 0189 — PyCSL Annotation Reference 3.1.14: String parameter type"""
_ = 0  # anchor
#@ requires s == "world"
#@ ensures \result == "hello"
def ignore_and_greet(s: str) -> str:
    """Takes a string parameter and returns a different string."""
    return "hello"

if __name__ == "__main__":
    assert ignore_and_greet("world") == "hello"
