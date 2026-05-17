""  # pycsl
import ast
from typing import List, Dict, Any
from dataclasses import dataclass

# Import the AST nodes from Module 2
from Module2_Parser import (
    CSLNode, Requires, Ensures, Assigns, LoopInvariant, LoopVariant,
    ClassInvariant, Label as CSLLabel, FunctionVariant, Diverges, Trusted,
    BoundedInt, RaisesDecl, GhostAssign
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

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        # Initialize the custom PyCSL fields on the Python AST node
        node.csl_requires = []
        node.csl_ensures = []
        node.csl_assigns = []
        node.csl_function_variants = []
        node.csl_diverges = False
        node.csl_trusted = False
        node.csl_bounded_int = None
        node.csl_raises = []

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
                elif isinstance(c, FunctionVariant):
                    node.csl_function_variants.append(c)
                elif isinstance(c, Diverges):
                    node.csl_diverges = True
                elif isinstance(c, Trusted):
                    node.csl_trusted = True
                elif isinstance(c, BoundedInt):
                    node.csl_bounded_int = c.bits
                elif isinstance(c, RaisesDecl):
                    node.csl_raises.append(c)

        if node.csl_function_variants and node.csl_diverges:
            raise ValueError(
                f"Function '{node.name}' (line {node.lineno}): "
                f"\\variant and \\diverges are contradictory — "
                f"one asserts termination, the other denies it."
            )

        # Continue traversing down the tree (in case of nested functions or loops)
        self.generic_visit(node)

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        node.csl_class_invariants = []

        if node.lineno in self.contracts_map:
            contracts = self.contracts_map[node.lineno]
            for c in contracts:
                if isinstance(c, ClassInvariant):
                    node.csl_class_invariants.append(c)

        self.generic_visit(node)

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
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

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
    def visit_For(self, node: ast.For) -> Any:
        """Attach loop_invariant and loop_variant contracts to for loops."""
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

    #@ \trusted
    #@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns \nothing
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

        # Step 4: Attach label nodes to their target statement nodes.
        # Labels appear in contracts_map keyed by the line of the labeled statement.
        labels_by_line: Dict[int, List[str]] = {}
        for line, nodes in contracts_map.items():
            names = [n.name for n in nodes if isinstance(n, CSLLabel)]
            if names:
                labels_by_line[line] = names

        if labels_by_line:
            for ast_node in ast.walk(python_ast):
                if isinstance(ast_node, ast.stmt) and hasattr(ast_node, 'lineno'):
                    labels = labels_by_line.get(ast_node.lineno)
                    if labels:
                        ast_node.csl_labels = labels

        # Step 5: Attach ghost assignments to their target statement nodes.
        ghosts_by_line: Dict[int, List[GhostAssign]] = {}
        for line, nodes in contracts_map.items():
            ghost_nodes = [n for n in nodes if isinstance(n, GhostAssign)]
            if ghost_nodes:
                ghosts_by_line[line] = ghost_nodes

        if ghosts_by_line:
            for ast_node in ast.walk(python_ast):
                if isinstance(ast_node, ast.stmt) and hasattr(ast_node, 'lineno'):
                    ghosts = ghosts_by_line.get(ast_node.lineno)
                    if ghosts:
                        ast_node.csl_ghost_assigns = ghosts

        return python_ast
