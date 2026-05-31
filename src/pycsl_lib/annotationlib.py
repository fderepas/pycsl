"""PyCSL mock for Python's annotationlib module — Functionality for introspecting annotations."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/annotationlib.html#annotationlib.annotations_to_string
#@ ensures len(\result) == len(annotations)
def annotations_to_string(annotations: int) -> int:
    """Mock: Convert an annotations dict containing runtime values to a dict containing only strings. If the values are not already s..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/annotationlib.html#annotationlib.call_annotate_function
# cite:_note: stub models the returned annotations dict as int; dict-shape contract exceeds current expressible surface
#@ requires format >= 1
#@ requires format <= 4
#@ ensures \result >= 0
def call_annotate_function(annotate: int, format: int, owner: int) -> int:
    """Mock: Call the :term:`annotate function` *annotate* with the given *format*, a member of the :class:`Format` enum, and return ..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/annotationlib.html#annotationlib.call_evaluate_function
#@ ensures True
def call_evaluate_function(evaluate: int, format: int, owner: int) -> int:
    """Mock: Call the :term:`evaluate function` *evaluate* with the given *format*, a member of the :class:`Format` enum, and return ..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/annotationlib.html#annotationlib.get_annotate_from_class_namespace
#@ ensures True
def get_annotate_from_class_namespace(namespace: int) -> int:
    """Mock: Retrieve the :term:`annotate function` from a class namespace dictionary *namespace*. Return :const:`!None` if the names..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/annotationlib.html#annotationlib.get_annotations
#@ requires format >= 1
#@ requires format <= 3
#@ ensures \result >= 0
def get_annotations(obj: int, globals: int, locals: int, eval_str: int, format: int) -> int:
    """Mock: Compute the annotations dict for an object. *obj* may be a callable, class, module, or other object with :attr:`~object...."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/annotationlib.html#annotationlib.type_repr
#@ ensures True
def type_repr(value: int) -> int:
    """Mock: Convert an arbitrary Python value to a format suitable for use by the :attr:`~Format.STRING` format. This calls :func:`r..."""
    return 0
