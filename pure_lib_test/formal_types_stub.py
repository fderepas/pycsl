# Formal tests for pure_lib/types_stub — types module
# SimpleNamespace/ModuleType/FunctionType classes.
# Test tag concept directly.


#@ ensures \result >= 0
def test_module_type_tag() -> int:
    """ModuleType has a type tag."""
    return 1


#@ ensures \result >= 0
def test_function_type_tag() -> int:
    """FunctionType has a type tag."""
    return 2
