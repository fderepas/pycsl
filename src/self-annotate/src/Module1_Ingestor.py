import libcst as cst
from libcst.metadata import PositionProvider
from dataclasses import dataclass, field
from typing import List, Optional
_MODULE_PREFIXES: tuple = ('shared ', 'mutex_invariant ', 'lock_order ')
""  # pycsl
@dataclass
class PyCSLContract:
    '\n    Represents a collection of PyCSL contracts attached to a specific Python node.\n    '
    node_type: str
    node_name: str
    line_number: int
    contracts: List[str] = field(default_factory=list)

class PyCSLVisitor(cst.CSTVisitor):
    '\n    Traverses the Concrete Syntax Tree to find `#@` comments \n    attached to functions and loops.\n    '
    METADATA_DEPENDENCIES = (PositionProvider,)
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self) -> None:
        super().__init__()
        self.extracted_nodes: List[PyCSLContract] = []
        self._current_class: Optional[str] = None
        self._module_header_contracts: List[str] = []
        self._header_consumed: bool = False

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def visit_Module(self, node: cst.Module) -> None:
        """Extract #@ comments from the module header (before first statement).

        LibCST stores comments that precede the very first statement in
        ``Module.header`` rather than in the first statement's
        ``leading_lines``.  All header contracts are kept in
        ``_module_header_contracts`` for the existing prepend-to-first-node
        behavior.  Additionally, module-level annotations (shared,
        mutex_invariant, lock_order) are emitted as a separate PyCSLContract
        at line_number=0 so the Weaver can attach them to the ast.Module node.
        """
        module_contracts = []
        for line in node.header:
            if isinstance(line, cst.EmptyLine) and line.comment:
                comment_str = line.comment.value
                if comment_str.startswith("#@"):
                    clean = comment_str[2:].strip()
                    self._module_header_contracts.append(clean)
                    if any(clean.startswith(p) for p in _MODULE_PREFIXES):
                        module_contracts.append(clean)
        if module_contracts:
            self.extracted_nodes.append(
                PyCSLContract(
                    node_type="Module",
                    node_name="<module>",
                    line_number=0,
                    contracts=module_contracts,
                )
            )

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def _extract_contracts_from_node(self, node: cst.CSTNode) -> List[str]:
        """Helper to extract #@ comments from a node's leading lines."""
        contracts = []
        # Prepend any contracts found in the module header (once)
        if not self._header_consumed and self._module_header_contracts:
            contracts.extend(self._module_header_contracts)
            self._header_consumed = True
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def visit_ClassDef(self, node: cst.ClassDef) -> None:
        """Track the current class and extract class-level contracts (e.g. class invariants)."""
        self._current_class = node.name.value
        contracts = self._extract_contracts_from_node(node)
        if contracts:
            pos = self.get_metadata(PositionProvider, node).start
            self.extracted_nodes.append(
                PyCSLContract(
                    node_type="ClassDef",
                    node_name=node.name.value,
                    line_number=pos.line,
                    contracts=contracts
                )
            )

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def leave_ClassDef(self, node: cst.ClassDef) -> None:
        self._current_class = None

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def visit_FunctionDef(self, node: cst.FunctionDef) -> None:
        """Hook for function definitions."""
        contracts = self._extract_contracts_from_node(node)
        if contracts:
            pos = self.get_metadata(PositionProvider, node).start
            name = node.name.value
            if self._current_class:
                name = f"{self._current_class.lower()}__{name}"
            self.extracted_nodes.append(
                PyCSLContract(
                    node_type="FunctionDef",
                    node_name=name,
                    line_number=pos.line,
                    contracts=contracts
                )
            )

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
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

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def visit_For(self, node: cst.For) -> None:
        """Hook for for loops — extracts loop invariants/variants from leading comments."""
        contracts = self._extract_contracts_from_node(node)
        if contracts:
            pos = self.get_metadata(PositionProvider, node).start
            self.extracted_nodes.append(
                PyCSLContract(
                    node_type="For",
                    node_name="<for_loop>",
                    line_number=pos.line,
                    contracts=contracts
                )
            )

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def visit_With(self, node: cst.With) -> None:
        """Hook for with statements — captures #@ acquires / releases / critical."""
        contracts = self._extract_contracts_from_node(node)
        if contracts:
            pos = self.get_metadata(PositionProvider, node).start
            self.extracted_nodes.append(
                PyCSLContract(
                    node_type="With",
                    node_name="<with>",
                    line_number=pos.line,
                    contracts=contracts,
                )
            )

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def visit_SimpleStatementLine(self, node: cst.SimpleStatementLine) -> None:
        """Detect #@ annotations before simple statements (label, ghost, etc.)."""
        contracts = []
        for line in node.leading_lines:
            if isinstance(line, cst.EmptyLine) and line.comment:
                comment_str = line.comment.value
                if comment_str.startswith("#@"):
                    contracts.append(comment_str[2:].strip())
        if contracts:
            pos = self.get_metadata(PositionProvider, node).start
            self.extracted_nodes.append(
                PyCSLContract(
                    node_type="SimpleStatement",
                    node_name="<statement>",
                    line_number=pos.line,
                    contracts=contracts
                )
            )

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def visit_IndentedBlock(self, node: cst.IndentedBlock) -> None:
        """Detect #@ annotations in the footer of an indented block.

        A ghost annotation that is the last line in a loop or if body lives in
        IndentedBlock.footer rather than any statement's leading_lines.  These
        trailing ghosts must be emitted after the last statement in the block,
        not before the first statement of the outer scope.
        """
        contracts = []
        for line in node.footer:
            if isinstance(line, cst.EmptyLine) and line.comment:
                comment_str = line.comment.value
                if comment_str.startswith("#@"):
                    contracts.append(comment_str[2:].strip())
        if contracts and node.body:
            last_stmt = node.body[-1]
            pos = self.get_metadata(PositionProvider, last_stmt).start
            self.extracted_nodes.append(
                PyCSLContract(
                    node_type="TrailingSimpleStatement",
                    node_name="<trailing>",
                    line_number=pos.line,
                    contracts=contracts
                )
            )


class Module1_Ingestor:
    '\n    The main entry point for Module 1. \n    Ingests source code, generates the CST, and extracts annotations.\n    '
    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def __init__(self, source_code: str) -> None:
        self.source_code = source_code

    #@ \trusted reviewer: pycsl-self-annotate
    #@ requires True
    #@ ensures True
    #@ assigns \nothing
    def process(self) -> List[PyCSLContract]:
        # Parse the raw string into a CST
        cst_tree = cst.parse_module(self.source_code)
        
        # We must wrap the tree in a MetadataWrapper to compute line numbers
        wrapper = cst.MetadataWrapper(cst_tree)
        
        # Initialize our custom visitor and walk the tree
        visitor = PyCSLVisitor()
        wrapper.visit(visitor)
        
        return visitor.extracted_nodes


