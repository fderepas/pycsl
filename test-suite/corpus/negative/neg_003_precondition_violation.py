# Negative test: precondition violation at call site
# Dynamic oracle should catch precondition failure

_ = 0  # anchor for LibCST leading_lines
#@ requires x > 0
#@ ensures \result > 0
def needs_positive(x: int) -> int:
    return x * 2

if __name__ == "__main__":
    print("needs_positive(-1) =", needs_positive(-1))  # precondition violated
