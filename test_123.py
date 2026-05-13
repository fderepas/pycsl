# main.py
import ast
from Module1_Ingestor import Module1_Ingestor
from Module2_Parser import Module2_Parser
from Module3_Weaver import Module3_Weaver

sample_code = """
#@ requires x > 0 and y > 0
#@ ensures \\result == x + y
#@ assigns \\nothing
def add_positive(x: int, y: int) -> int:
    return x + y

def sum_n(n: int) -> int:
    total = 0
    i = 0
    #@ loop invariant total >= 0
    #@ loop variant n - i
    while i < n:
        total += i
        i += 1
    return total
"""

if __name__ == "__main__":
    print("Starting PyCSL Frontend Pipeline...\n")

    # [Module 1] Extract #@ comments using LibCST
    ingestor = Module1_Ingestor(sample_code)
    extracted_data = ingestor.process()

    # [Module 2] Initialize the Lark Parser
    parser = Module2_Parser()

    # [Module 3] Weave the parsed contracts into the standard Python AST
    weaver = Module3_Weaver(sample_code, extracted_data, parser)
    unified_ast = weaver.process()

    # Verify the results by walking the newly augmented Python AST
    print("--- Unified Annotated AST (AAST) ---")
    for node in ast.walk(unified_ast):
        if isinstance(node, ast.FunctionDef):
            print(f"\nFunction: {node.name}()")
            print(f"  Requires:  {node.csl_requires}")
            print(f"  Ensures:   {node.csl_ensures}")
            print(f"  Assigns:   {node.csl_assigns}")
            
        elif isinstance(node, ast.While):
            print(f"\nWhile Loop at line {node.lineno}")
            print(f"  Invariant: {node.csl_invariants}")
            print(f"  Variant:   {node.csl_variants}")
