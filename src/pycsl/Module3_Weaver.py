import ast
from typing import List, Dict, Any
from dataclasses import dataclass

# Import the AST nodes from Module 2
from Module2_Parser import (
    CSLNode, Requires, Ensures, Assigns, LoopInvariant, LoopVariant,
    ClassInvariant, Label as CSLLabel, FunctionVariant, Diverges, Trusted,
    GhostAssignDecl, RaisesDecl, BoundedIntDecl,
    SharedDecl, ThreadEntry, Acquires, Releases, CriticalSection,
    MutexInvariant, LockOrder,
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
    def __init__(self, contracts_map: Dict[int, List[CSLNode]]) -> None:
        # We index the parsed contracts by the line number of the target node
        self.contracts_map = contracts_map

    def visit_FunctionDef(self, node: ast.FunctionDef) -> Any:
        # Initialize the custom PyCSL fields on the Python AST node
        node.csl_requires = []
        node.csl_ensures = []
        node.csl_assigns = []
        node.csl_function_variants = []
        node.csl_diverges = False
        node.csl_trusted = False
        node.csl_raises = []
        node.csl_bounded_int = None
        node.csl_thread_entry = False

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
                elif isinstance(c, RaisesDecl):
                    node.csl_raises.append(c)
                elif isinstance(c, BoundedIntDecl):
                    node.csl_bounded_int = c.size
                elif isinstance(c, ThreadEntry):
                    node.csl_thread_entry = True

        if node.csl_function_variants and node.csl_diverges:
            raise ValueError(
                f"Function '{node.name}' (line {node.lineno}): "
                f"\\variant and \\diverges are contradictory — "
                f"one asserts termination, the other denies it."
            )

        # Continue traversing down the tree (in case of nested functions or loops)
        self.generic_visit(node)

    def visit_Module(self, node: ast.Module) -> Any:
        """Attach module-level concurrency annotations (shared, mutex_invariant, lock_order)."""
        node.csl_shared_decls = []
        node.csl_mutex_invariants = {}
        node.csl_lock_order = None

        if 0 in self.contracts_map:
            for c in self.contracts_map[0]:
                if isinstance(c, SharedDecl):
                    node.csl_shared_decls.append(c)
                elif isinstance(c, MutexInvariant):
                    node.csl_mutex_invariants[c.mutex] = c.expr
                elif isinstance(c, LockOrder):
                    node.csl_lock_order = c

        self.generic_visit(node)

    def visit_With(self, node: ast.With) -> Any:
        """Attach acquire/release/critical annotations to with statements."""
        node.csl_critical_mutex = None
        node.csl_acquires = None
        node.csl_releases = None

        if node.lineno in self.contracts_map:
            for c in self.contracts_map[node.lineno]:
                if isinstance(c, CriticalSection):
                    node.csl_critical_mutex = c.mutex
                elif isinstance(c, Acquires):
                    node.csl_acquires = c.mutex
                elif isinstance(c, Releases):
                    node.csl_releases = c.mutex

        self.generic_visit(node)

    def visit_ClassDef(self, node: ast.ClassDef) -> Any:
        node.csl_class_invariants = []

        if node.lineno in self.contracts_map:
            contracts = self.contracts_map[node.lineno]
            for c in contracts:
                if isinstance(c, ClassInvariant):
                    node.csl_class_invariants.append(c)

        self.generic_visit(node)

    def visit_While(self, node: ast.While) -> Any:
        # Initialize the custom PyCSL fields
        node.csl_invariants = []
        node.csl_variants = []
        node.csl_ghost_assigns = []

        if node.lineno in self.contracts_map:
            contracts = self.contracts_map[node.lineno]
            for c in contracts:
                if isinstance(c, LoopInvariant):
                    node.csl_invariants.append(c)
                elif isinstance(c, LoopVariant):
                    node.csl_variants.append(c)
                elif isinstance(c, GhostAssignDecl):
                    node.csl_ghost_assigns.append(c)

        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> Any:
        """Attach loop_invariant and loop_variant contracts to for loops."""
        node.csl_invariants = []
        node.csl_variants = []
        node.csl_ghost_assigns = []

        if node.lineno in self.contracts_map:
            contracts = self.contracts_map[node.lineno]
            for c in contracts:
                if isinstance(c, LoopInvariant):
                    node.csl_invariants.append(c)
                elif isinstance(c, LoopVariant):
                    node.csl_variants.append(c)
                elif isinstance(c, GhostAssignDecl):
                    node.csl_ghost_assigns.append(c)

        self.generic_visit(node)

# ---------------------------------------------------------
# 2. The Weaver Interface
# ---------------------------------------------------------

class Module3_Weaver:
    """
    Coordinates the standard AST generation and the injection of contracts.
    """
    def __init__(self, source_code: str, extracted_data: List[PyCSLContract], parser_module: Any) -> None:
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

        # Step 3b: Consolidate module-level concurrency annotations from all contracts.
        # SharedDecl, MutexInvariant, LockOrder may appear anywhere in the file
        # (module header or as leading_lines of any statement), so we scan globally.
        if not hasattr(python_ast, 'csl_shared_decls'):
            python_ast.csl_shared_decls = []
        if not hasattr(python_ast, 'csl_mutex_invariants'):
            python_ast.csl_mutex_invariants = {}
        if not hasattr(python_ast, 'csl_lock_order'):
            python_ast.csl_lock_order = None
        seen_shared = {d.variable for d in python_ast.csl_shared_decls}
        for nodes in contracts_map.values():
            for n in nodes:
                if isinstance(n, SharedDecl) and n.variable not in seen_shared:
                    python_ast.csl_shared_decls.append(n)
                    seen_shared.add(n.variable)
                elif isinstance(n, MutexInvariant) and n.mutex not in python_ast.csl_mutex_invariants:
                    python_ast.csl_mutex_invariants[n.mutex] = n.expr
                elif isinstance(n, LockOrder) and python_ast.csl_lock_order is None:
                    python_ast.csl_lock_order = n

        # Step 4: Attach label nodes to their target statement nodes.
        # Labels appear in contracts_map keyed by the line of the labeled statement.
        labels_by_line: Dict[int, List[str]] = {}
        ghost_assigns_by_line: Dict[int, List] = {}
        for line, nodes in contracts_map.items():
            names = [n.name for n in nodes if isinstance(n, CSLLabel)]
            if names:
                labels_by_line[line] = names
            ghosts = [n for n in nodes if isinstance(n, GhostAssignDecl)]
            if ghosts:
                ghost_assigns_by_line[line] = ghosts

        if labels_by_line or ghost_assigns_by_line:
            for ast_node in ast.walk(python_ast):
                if isinstance(ast_node, ast.stmt) and hasattr(ast_node, 'lineno'):
                    labels = labels_by_line.get(ast_node.lineno)
                    if labels:
                        ast_node.csl_labels = labels
                    ghosts = ghost_assigns_by_line.get(ast_node.lineno)
                    if ghosts:
                        existing = getattr(ast_node, 'csl_ghost_assigns', [])
                        ast_node.csl_ghost_assigns = existing + ghosts

        return python_ast
