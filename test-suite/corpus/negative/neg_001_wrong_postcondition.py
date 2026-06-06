# Negative test: postcondition is intentionally wrong
# This should FAIL on dynamic oracle (assertion error)
# Static oracle should also report FAIL (Invalid goals)

_ = 0  # anchor for LibCST leading_lines
#@ ensures \result == x + 2
def wrong_increment(x: int) -> int:
    return x + 1

if __name__ == "__main__":
    print("wrong_increment(5) =", wrong_increment(5))
