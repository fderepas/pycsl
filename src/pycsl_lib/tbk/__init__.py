# Pure model for traceback — stack trace utilities
# Models as line-count based formatting.


#@ requires depth >= 0
#@ ensures \result >= depth
def format_exc(depth: int) -> int:
    """Format exception traceback. Returns line count >= depth."""
    return depth


#@ requires depth >= 0
#@ ensures \result >= depth
def format_tb(depth: int) -> int:
    """Format traceback. Returns line count >= depth."""
    return depth


#@ requires depth >= 0
#@ ensures \result >= 0
def print_exc(depth: int) -> int:
    """Print exception to stderr. Returns 0."""
    return 0


#@ requires depth >= 0
#@ ensures \result >= depth
def format_stack(depth: int) -> int:
    """Format current stack. Returns line count >= depth."""
    return depth


#@ requires limit >= 0
#@ ensures \result >= 0
#@ ensures \result <= limit
def extract_tb(limit: int) -> int:
    """Extract traceback entries up to limit."""
    return limit


#@ requires limit >= 0
#@ ensures \result >= 0
#@ ensures \result <= limit
def extract_stack(limit: int) -> int:
    """Extract stack entries up to limit."""
    return limit
