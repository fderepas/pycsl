"""PyCSL mock for Python's pickletools module — Contains extensive comments about the pickle protocols and."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def dis(pickle: int, out: int, memo: int, indentlevel: int, annotate: int) -> int:
    """Mock: Outputs a symbolic disassembly of the pickle to the file-like object *out*, defaulting to ``sys.stdout``.  *pickle* can ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def genops(pickle: int) -> int:
    """Mock: Provides an :term:`iterator` over all of the opcodes in a pickle, returning a sequence of ``(opcode, arg, pos)`` triples..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def optimize(picklestring: int) -> int:
    """Mock: Returns a new equivalent pickle string after eliminating unused ``PUT`` opcodes. The optimized pickle is shorter, takes ..."""
    return 0
