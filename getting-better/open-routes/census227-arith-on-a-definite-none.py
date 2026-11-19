"""Route #227 population census: arithmetic / order comparison on a DEFINITELY-None operand.

Approximates Module 6's `_erased_truthy_locals` linear recorder: a name is definitely-None
after `x = None` and stops being so on any rebinding. Flags a BinOp with an arithmetic or
order operator one of whose operands is (a) such a name, or (b) a literal `None`.
Also reports the literal-None case separately, and unary minus as residue.
"""
import ast, sys, os

ARITH = {ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
         ast.LShift, ast.RShift, ast.BitAnd, ast.BitOr, ast.BitXor}
ORDER = {ast.Lt, ast.LtE, ast.Gt, ast.GtE}

hits = []

def is_none(n):
    return isinstance(n, ast.Constant) and n.value is None

class FnScan(ast.NodeVisitor):
    def __init__(self, path, fname):
        self.path, self.fname = path, fname
        self.none_names = set()
    def _rec(self, stmt):
        # linear recorder over a statement list
        pass
    def visit_Assign(self, node):
        # visit the VALUE first (reads happen before the rebinding)
        self.visit(node.value)
        for t in node.targets:
            if isinstance(t, ast.Name):
                if is_none(node.value):
                    self.none_names.add(t.id)
                else:
                    self.none_names.discard(t.id)
    def visit_AnnAssign(self, node):
        if node.value is not None:
            self.visit(node.value)
            if isinstance(node.target, ast.Name):
                if is_none(node.value):
                    self.none_names.add(node.target.id)
                else:
                    self.none_names.discard(node.target.id)
    def _flag(self, node, kind, what):
        hits.append((self.path, self.fname, getattr(node, 'lineno', 0), kind, what))
    def visit_BinOp(self, node):
        if type(node.op) in ARITH:
            for side in (node.left, node.right):
                if is_none(side):
                    self._flag(node, "ARITH-literal-None", ast.dump(node.op).split('(')[0])
                elif isinstance(side, ast.Name) and side.id in self.none_names:
                    self._flag(node, "ARITH-none-local", f"{side.id} {type(node.op).__name__}")
        self.generic_visit(node)
    def visit_Compare(self, node):
        ops = [type(o) for o in node.ops]
        if any(o in ORDER for o in ops):
            for side in [node.left] + list(node.comparators):
                if is_none(side):
                    self._flag(node, "ORDER-literal-None", "order-cmp")
                elif isinstance(side, ast.Name) and side.id in self.none_names:
                    self._flag(node, "ORDER-none-local", side.id)
        self.generic_visit(node)
    def visit_UnaryOp(self, node):
        if isinstance(node.op, (ast.USub, ast.UAdd, ast.Invert)):
            s = node.operand
            if is_none(s):
                self._flag(node, "UNARY-literal-None", "usub")
            elif isinstance(s, ast.Name) and s.id in self.none_names:
                self._flag(node, "UNARY-none-local", s.id)
        self.generic_visit(node)
    def visit_FunctionDef(self, node):
        sub = FnScan(self.path, self.fname + "." + node.name)
        for st in node.body:
            sub.visit(st)
    visit_AsyncFunctionDef = visit_FunctionDef

roots = sys.argv[1:]
nfiles = 0
for root in roots:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in ('.git', '.venv', '__pycache__')]
        for fn in filenames:
            if not fn.endswith('.py'):
                continue
            p = os.path.join(dirpath, fn)
            try:
                tree = ast.parse(open(p, encoding='utf-8', errors='replace').read())
            except Exception:
                continue
            nfiles += 1
            top = FnScan(p, "")
            for st in tree.body:
                top.visit(st)
print(f"files scanned: {nfiles}")
from collections import Counter
c = Counter(h[3] for h in hits)
print("hits by kind:", dict(c) if c else "NONE")
for h in hits[:40]:
    print("  ", h)
print("TOTAL HITS:", len(hits))
