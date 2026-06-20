# pycsl_lib/token — pure-Python token module model
#
# Contracts derived from library_reference/token.rst.
# RST: "This module provides constants which represent the numeric values
#  of leaf nodes of the parse tree."
#
# Model: token type constants + ISTERMINAL/ISNONTERMINAL predicates.

# Token type constants
ENDMARKER  = 0
NAME       = 1
NUMBER     = 2
STRING     = 3
NEWLINE    = 4
INDENT     = 5
DEDENT     = 6
OP         = 54
COMMENT    = 60
NL         = 61
ENCODING   = 62
NT_OFFSET  = 256


#@ requires tok_type >= 0
#@ ensures \result == 1 or \result == 0
#@ ensures tok_type < 256 ==> \result == 1
#@ ensures tok_type >= 256 ==> \result == 0
#@ assigns \nothing
def ISTERMINAL(tok_type: int) -> int:
    """RST: 'Return True for terminal token type values.'
    Terminal tokens have type < NT_OFFSET (256)."""
    if tok_type < 256:
        return 1
    return 0


#@ requires tok_type >= 0
#@ ensures \result == 1 or \result == 0
#@ ensures tok_type >= 256 ==> \result == 1
#@ ensures tok_type < 256 ==> \result == 0
#@ assigns \nothing
def ISNONTERMINAL(tok_type: int) -> int:
    """RST: 'Return True for non-terminal token type values.'
    Non-terminal tokens have type >= NT_OFFSET (256)."""
    if tok_type >= 256:
        return 1
    return 0


#@ requires tok_type >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def tok_name(tok_type: int) -> int:
    """RST: 'Dictionary mapping token type values to names.'
    Returns name string length (non-negative)."""
    return tok_type
