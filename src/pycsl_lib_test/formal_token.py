# Formal tests for pycsl_lib/token
from pycsl_lib.token import ISTERMINAL, ISNONTERMINAL


#@ requires tok_type >= 0
#@ ensures \result == 1 or \result == 0
#@ ensures tok_type < 256 ==> \result == 1
#@ ensures tok_type >= 256 ==> \result == 0
def test_isterminal(tok_type: int) -> int:
    """ISTERMINAL correct classification."""
    return ISTERMINAL(tok_type)


#@ requires tok_type >= 0
#@ ensures \result == 1 or \result == 0
#@ ensures tok_type >= 256 ==> \result == 1
#@ ensures tok_type < 256 ==> \result == 0
def test_isnonterminal(tok_type: int) -> int:
    """ISNONTERMINAL correct classification."""
    return ISNONTERMINAL(tok_type)
