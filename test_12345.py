import ast
from Module1_Ingestor import Module1_Ingestor
from Module2_Parser import Module2_Parser
from Module3_Weaver import Module3_Weaver
from Module4_SemanticAnalyzer import Module4_SemanticAnalyzer, PyCSLSemanticError
from Module5_IREmitter import Module5_IREmitter

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

    # [Modules 1-3] Ingest, Parse, and Weave
    ingestor = Module1_Ingestor(sample_code)
    extracted_data = ingestor.process()

    parser = Module2_Parser()
    weaver = Module3_Weaver(sample_code, extracted_data, parser)
    unified_ast = weaver.process()

    # [Module 4] Semantic Analysis
    analyzer = Module4_SemanticAnalyzer()
    try:
        validated_ast = analyzer.process(unified_ast)
        print("Semantic Analysis Passed!\n")
        
        # [Module 5] IR Generation
        emitter = Module5_IREmitter(validated_ast)
        json_ir = emitter.generate_json()
        
        print("--- Generated JSON IR ---")
        print(json_ir)
        
        # Optionally, write it to a file
        with open("pycsl_ir.json", "w") as f:
            f.write(json_ir)
            
    except PyCSLSemanticError as e:
        print(f"\n[!] SEMANTIC ERROR: {e}")
