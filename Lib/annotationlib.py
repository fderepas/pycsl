"""PyCSL mock for Python's annotationlib module — Functionality for introspecting annotations."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def annotations_to_string(annotations: int) -> int:
    """Mock: Convert an annotations dict containing runtime values to a dict containing only strings. If the values are not already s..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def call_annotate_function(annotate: int, format: int, owner: int) -> int:
    """Mock: Call the :term:`annotate function` *annotate* with the given *format*, a member of the :class:`Format` enum, and return ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def call_evaluate_function(evaluate: int, format: int, owner: int) -> int:
    """Mock: Call the :term:`evaluate function` *evaluate* with the given *format*, a member of the :class:`Format` enum, and return ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_annotate_from_class_namespace(namespace: int) -> int:
    """Mock: Retrieve the :term:`annotate function` from a class namespace dictionary *namespace*. Return :const:`!None` if the names..."""
    return 0

#@ \trusted
#@ ensures \result == 0 or \result == 1
def get_annotations(obj: int, globals: int, locals: int, eval_str: int, format: int) -> int:
    """Mock: Compute the annotations dict for an object. *obj* may be a callable, class, module, or other object with :attr:`~object...."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def type_repr(value: int) -> int:
    """Mock: Convert an arbitrary Python value to a format suitable for use by the :attr:`~Format.STRING` format. This calls :func:`r..."""
    return 0
