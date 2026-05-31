"""PyCSL mock for Python's dis module — Disassembler for Python bytecode."""
_ = 0  # anchor

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dis.html#dis.code_info
#@ ensures True
def code_info(x: int) -> int:
    """Mock: Return a formatted multi-line string with detailed code object information for the supplied function, generator, asynchr..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dis.html#dis.show_code
#@ ensures True
#@ assigns \nothing
def show_code(x: int, file: int) -> int:
    """Mock: Print detailed code object information for the supplied function, method, source code string or code object to *file* (o..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dis.html#dis.dis
#@ ensures True
#@ assigns \nothing
def dis(x: int, file: int, depth: int, show_caches: int, __adaptive: int, show_offsets: int, show_positions: int) -> int:
    """Mock: Disassemble the *x* object.  *x* can denote either a module, a class, a method, a function, a generator, an asynchronous..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dis.html#dis.distb
#@ ensures True
def distb(tb: int, file: int, show_caches: int, adaptive: int, __show_offset: int, show_positions: int) -> int:
    """Mock: Disassemble the top-of-stack function of a traceback, using the last traceback if none was passed.  The instruction caus..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dis.html#dis.disassemble
#@ ensures True
def disassemble(code: int, lasti: int, file: int, show_caches: int, __adaptive: int, show_offsets: int, show_positions: int) -> int:
    """Mock: show_offsets=False, show_positions=False) Disassemble a code object, indicating the last instruction if *lasti* was prov..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dis.html#dis.get_instructions
#@ ensures True
def get_instructions(x: int, first_line: int, show_caches: int, adaptive: int) -> int:
    """Mock: Return an iterator over the instructions in the supplied function, method, source code string or code object. The iterat..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dis.html#dis.findlinestarts
#@ ensures \result >= 0
def findlinestarts(code: int) -> int:
    """Mock: This generator function uses the :meth:`~codeobject.co_lines` method of the :ref:`code object <code-objects>` *code* to ..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dis.html#dis.findlabels
#@ ensures \result >= 0
def findlabels(code: int) -> int:
    """Mock: Detect all offsets in the raw compiled bytecode string *code* which are jump targets, and return a list of these offsets..."""
    return 0

#@ \trusted reviewer: python-stdlib
# cite: https://docs.python.org/3/library/dis.html#dis.stack_effect
#@ ensures True
def stack_effect(opcode: int, oparg: int, jump: int) -> int:
    """Mock: Compute the stack effect of *opcode* with argument *oparg*. If the code has a jump target and *jump* is ``True``, :func:..."""
    return 0
