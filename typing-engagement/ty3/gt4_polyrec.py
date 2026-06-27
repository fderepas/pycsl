"""TY3 GT4 loud-fail — polymorphic recursion must be rejected.

A generic function `f[T]` that calls `f[T]()` (with the TypeVar ITSELF, not a
concrete type) is polymorphic recursion — monomorphization would require
specializing `f` for infinitely many types. The pass must LOUD-FAIL with
PYCSL-TY3-GT4.
"""
_ = 0
def f[T]() -> None:
    f[T]()

if __name__ == "__main__":
    f[int]()
