"""PyCSL mock for lark.

Provides trusted stubs for the Lark parsing toolkit.
Lark parser, Token, Tree, and Transformer modelled as classes.
"""
_ = 0  # anchor

# ── LarkParserObj class ─────────────────────────────────────────────

""  # pycsl
#@ class invariant self._ready >= 0
class LarkParserObj:
    def __init__(self):
        self._ready = 1

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def lark_parse(self, text: int) -> int:
        return 0

# ── TokenObj class ──────────────────────────────────────────────────

#@ class invariant self._type >= 0
class TokenObj:
    def __init__(self):
        self._type = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._type
    #@ assigns \nothing
    def token_type(self) -> int:
        return self._type

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def token_value(self) -> int:
        return 0

# ── TreeObj class ───────────────────────────────────────────────────

#@ class invariant self._children_count >= 0
class TreeObj:
    def __init__(self):
        self._children_count = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def data(self) -> int:
        return 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures \result == self._children_count
    #@ assigns \nothing
    def children_count(self) -> int:
        return self._children_count

# ── TransformerObj class ────────────────────────────────────────────

#@ class invariant self._transforms >= 0
class TransformerObj:
    def __init__(self):
        self._transforms = 0

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures self._transforms == \old(self._transforms) + 1
    #@ assigns self._transforms
    def transform(self, tree: int) -> int:
        self._transforms += 1
        return 0

# ── Standalone functions ────────────────────────────────────────────

#@ \trusted
#@ ensures \result >= 0
def v_args(inline: int) -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def LarkError() -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def UnexpectedInput() -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def UnexpectedToken() -> int:
    return 0

#@ \trusted
#@ ensures \result >= 0
def UnexpectedCharacters() -> int:
    return 0
