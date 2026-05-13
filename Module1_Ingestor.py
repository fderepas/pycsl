import libcst as cst
from libcst.metadata import PositionProvider
from dataclasses import dataclass, field
from typing import List

# ---------------------------------------------------------
# 1. Data Structures
# ---------------------------------------------------------

@dataclass
class PyCSLContract:
    """
    Represents a collection of PyCSL contracts attached to a specific Python node.
    """
    node_type: str          # e.g., 'FunctionDef' or 'While'
    node_name: str          # e.g., 'add_positive' or '<while_loop>'
    line_number: int        # Where the node starts (useful for error reporting later)
    contracts: List[str] = field(default_factory=list) # The raw string contracts

# ---------------------------------------------------------
# 2. The CST Visitor
# ---------------------------------------------------------

class PyCSLVisitor(cst.CSTVisitor):
    """
    Traverses the Concrete Syntax Tree to find `#@` comments 
    attached to functions and loops.
    """
    # We require PositionProvider to grab line numbers for our frontend errors
    METADATA_DEPENDENCIES = (PositionProvider,)

    def __init__(self):
        super().__init__()
        self.extracted_nodes: List[PyCSLContract] = []

    def _extract_contracts_from_node(self, node: cst.CSTNode) -> List[str]:
        """Helper to extract #@ comments from a node's leading lines."""
        contracts = []
        # In LibCST, comments before a statement are stored in 'leading_lines'
        if hasattr(node, 'leading_lines'):
            for line in node.leading_lines:
                if isinstance(line, cst.EmptyLine) and line.comment:
                    comment_str = line.comment.value
                    if comment_str.startswith("#@"):
                        # Strip the '#@' marker and any surrounding whitespace
                        clean_contract = comment_str[2:].strip()
                        contracts.append(clean_contract)
        return contracts

    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        """Hook for function definitions."""
        contracts = self._extract_contracts_from_node(node)
        if contracts:
            pos = self.get_metadata(PositionProvider, node).start
            self.extracted_nodes.append(
                PyCSLContract(
                    node_type="FunctionDef",
                    node_name=node.name.value,
                    line_number=pos.line,
                    contracts=contracts
                )
            )

    def visit_While(self, node: cst.While) -> None:
        """Hook for while loops."""
        contracts = self._extract_contracts_from_node(node)
        if contracts:
            pos = self.get_metadata(PositionProvider, node).start
            self.extracted_nodes.append(
                PyCSLContract(
                    node_type="While",
                    node_name="<while_loop>",
                    line_number=pos.line,
                    contracts=contracts
                )
            )

# ---------------------------------------------------------
# 3. The Ingestion Engine
# ---------------------------------------------------------

class Module1_Ingestor:
    """
    The main entry point for Module 1. 
    Ingests source code, generates the CST, and extracts annotations.
    """
    def __init__(self, source_code: str):
        self.source_code = source_code

    def process(self) -> List[PyCSLContract]:
        # Parse the raw string into a CST
        cst_tree = cst.parse_module(self.source_code)
        
        # We must wrap the tree in a MetadataWrapper to compute line numbers
        wrapper = cst.MetadataWrapper(cst_tree)
        
        # Initialize our custom visitor and walk the tree
        visitor = PyCSLVisitor()
        wrapper.visit(visitor)
        
        return visitor.extracted_nodes
