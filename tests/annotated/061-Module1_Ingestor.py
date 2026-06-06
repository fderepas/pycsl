import libcst as cst
from libcst.metadata import PositionProvider
from dataclasses import dataclass, field
from typing import List, Optional

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
        self._current_class: Optional[str] = None
        self._module_header_contracts: List[str] = []
        self._header_consumed: bool = False

#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns self._module_header_contracts
def visit_Module(self, node: cst.Module) -> None:
    pass
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns self._header_consumed
    def _extract_contracts_from_node(self, node: cst.CSTNode) -> List[str]:
        pass
#@ requires 1 == 1
#@ ensures 1 == 1
#@ ensures 1 == 1
    #@ assigns self._current_class, self.extracted_nodes
    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        pass
#@ requires 1 == 1
    #@ ensures 1 == 1
    #@ assigns self._current_class
    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        pass
#@ requires 1 == 1
#@ ensures 1 == 1
#@ ensures 1 == 1
    #@ assigns self.extracted_nodes
    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        pass
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns self.extracted_nodes
    def visit_While(self, node: cst.While) -> None:
        pass
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns self.extracted_nodes, self._header_consumed
    def visit_For(self, node: cst.For) -> None:
        pass
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns self.extracted_nodes
    def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine) -> None:
        pass
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

#@ requires 1 == 1
#@ ensures 1 == 1
    #@ assigns \nothing
    def process(self) -> List[PyCSLContract]:
        pass
