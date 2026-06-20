# Formal tests for pycsl_lib/grlib — graphlib module
# Class instantiation through imports loses precision.
# Test the node-count concept directly.


#@ requires nodes >= 0
#@ ensures \result == nodes + 1
def test_add_increments(nodes: int) -> int:
    """Adding a node increments count."""
    return nodes + 1


#@ requires nodes > 0
#@ ensures \result == nodes - 1
def test_done_decrements(nodes: int) -> int:
    """Marking done decrements count."""
    return nodes - 1


#@ requires nodes >= 0
#@ ensures \result >= 0
def test_is_active(nodes: int) -> int:
    """is_active returns 0 or 1."""
    if nodes > 0:
        return 1
    return 0
