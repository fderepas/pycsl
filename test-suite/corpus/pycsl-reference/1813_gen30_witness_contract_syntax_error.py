r"""Test 1813 — WITNESS: a malformed `#@` CONTRACT is a hard parse error.

`Module2_Parser.parse_contract` wraps every `_ContractSyntaxError` into the user-facing
"PyCSL Syntax Error around line N", quoting the contract text and the tokenizer's
complaint. It is one of the most user-visible refusals in the system and it had NO WITNESS:
measured, ZERO of the 841 censused expected-FAIL witnesses produced it, because every
corpus contract is well-formed by construction.

A gate that has never seen its most common refusal fire has not been tested on the path
users take first.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires n >= = 0
#@ ensures \result >= 0
def f(n: int) -> int:
    return n
