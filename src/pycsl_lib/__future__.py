"""PyCSL mock for Python's __future__ module.

Provides trusted stubs for future statement definitions.
"""
_ = 0  # anchor

# ── Feature flags ───────────────────────────────────────────────────

nested_scopes = 0
generators = 0
division = 0
absolute_import = 0
with_statement = 0
print_function = 0
unicode_literals = 0
generator_stop = 0
annotations = 0
barry_as_FLUFL = 0

# ── _Feature methods ───────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/__future__.html#future-feature-flags
#@ requires True
#@ ensures \result >= 0
def Feature_getOptionalRelease(self: int) -> int:
    """Mock: return release when the feature was first accepted."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://github.com/python/cpython/blob/main/Lib/__future__.py
#@ requires True
#@ ensures True
def Feature_getMandatoryRelease(self: int) -> int:
    """Mock: return release when the feature became mandatory."""
    return 0

# ── _Feature attributes ────────────────────────────────────────────

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/__future__.html#future-statement-semantics
#@ requires True
#@ ensures \result >= 0
def Feature_compiler_flag(self: int) -> int:
    """Mock: return the compiler flag bitfield for the feature."""
    return 0
