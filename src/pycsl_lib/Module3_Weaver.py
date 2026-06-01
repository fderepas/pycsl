"""PyCSL mock for Module3_Weaver."""
_ = 0  # anchor

# ── PyCSLWeaverObj class ────────────────────────────────────────────

""  # pycsl
#@ class invariant self._injected >= 0
class PyCSLWeaverObj:
    def __init__(self):
        self._injected = 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/ast.py
#@ requires True
#@ ensures True
#@ assigns self._injected
    def visit_functiondef(self, node: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/ast.py
#@ requires True
#@ ensures True
#@ assigns self._injected
    def visit_classdef(self, node: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/ast.py
#@ requires True
#@ ensures True
#@ assigns self._injected
    def visit_while(self, node: int) -> int:
        return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/ast.py
#@ requires True
#@ ensures True
#@ assigns self._injected
    def visit_for(self, node: int) -> int:
        return 0

# ── Module3WeaverObj class ──────────────────────────────────────────

#@ class invariant self._processed >= 0
class Module3WeaverObj:
    def __init__(self):
        self._processed = 0

    #@ \trusted
    #@ requires self._processed == 0
    #@ ensures self._processed == 1
    #@ assigns self._processed
    def process(self) -> int:
        self._processed = 1
        return 0
