import ast
from typing import List, Dict, Any
from dataclasses import dataclass

# Import the AST nodes from Module 2
from Module2_Parser import (
    CSLNode, Requires, Ensures, Assigns, LoopInvariant, LoopVariant
)
from Module1_Ingestor import PyCSLContract

# ---------------------------------------------------------
# 1. The AST Weaver
# ---------------------------------------------------------

class PyCSLWeaver(ast.NodeVisitor):
    """
    Traverses the standard Python AST and injects parsed contract nodes 
    directly into the AST objects.
    """
    def __init__(self, contracts_map: Dict[int, List[CSLNode]]):
        # We index the parsed contracts by the line number of the target node
        self.contracts_map = contracts_map

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        # Initialize the custom PyCSL fields on the Python AST node
        node.csl_requires = []
        node.csl_ensures = []
        node.csl_assigns = []

        # In standard `ast`, node.lineno points to the 'def' keyword.
        # We check if we have any parsed contracts for this line.
        if node.lineno in self.contracts_map:
            contracts = self.contracts_map[node.lineno]
            for c in contracts:
                if isinstance(c, Requires):
                    node.csl_requires.append(c)
                elif isinstance(c, Ensures):
                    node.csl_ensures.append(c)
                elif isinstance(c, Assigns):
                    node.csl_assigns.append(c)

        # Continue traversing down the tree (in case of nested functions or loops)
        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> Any:
        # Initialize the custom PyCSL fields
        node.csl_invariants = []
        node.csl_variants = []

        if node.lineno in self.contracts_map:
            contracts = self.contracts_map[node.lineno]
            for c in contracts:
                if isinstance(c, LoopInvariant):
                    node.csl_invariants.append(c)
                elif isinstance(c, LoopVariant):
                    node.csl_variants.append(c)

        self.generic_visit(node)

# ---------------------------------------------------------
# 2. The Weaver Interface
# ---------------------------------------------------------

class Module3_Weaver:
    """
    Coordinates the standard AST generation and the injection of contracts.
    """
    def __init__(self, source_code: str, extracted_data: List[PyCSLContract], parser_module):
        self.source_code = source_code
        self.extracted_data = extracted_data
        self.parser_module = parser_module

    def process(self) -> ast.AST:
        # Step 1: Parse all extracted strings into Contract AST nodes
        # We create a mapping: line_number -> List[CSLNode]
        contracts_map: Dict[int, List[CSLNode]] = {}
        
        for extraction in self.extracted_data:
            parsed_nodes = self.parser_module.parse_node_contracts(
                extraction.contracts, 
                extraction.line_number
            )
            contracts_map[extraction.line_number] = parsed_nodes

        # Step 2: Generate the standard Python AST
        python_ast = ast.parse(self.source_code)

        # Step 3: Weave the Contract AST nodes into the Python AST
        weaver = PyCSLWeaver(contracts_map)
        weaver.visit(python_ast)

        return python_ast
