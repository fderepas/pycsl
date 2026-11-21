#!/usr/bin/env -S python3 -W ignore
"""Cheap AST prototype of candidate SYSTEMATIC refuse-by-default rules (systematic-soundness-r3).

Each rule is a predicate over one source file's module AST: it returns the list of sites
(line, why) the rule would REFUSE. The predicate is what a Module-3 inline pre-pass would
test; it reads only the program text (no type inference), so it over-approximates nothing
the front end could not also see. Run over a population of files, it gives:
  - over-refusal: how many currently-PASS files the rule would refuse;
  - catch: how many confirmed red-team probes the rule would refuse.
Usage: proto_rules.py [--rules R1,R2] [--detail] FILE...   -> TSV: file  rule  nsites  first-site
"""
import ast, sys, os

import builtins as _b
BUILTIN_EXC = {n for n in dir(_b) if isinstance(getattr(_b, n), type) and issubclass(getattr(_b, n), BaseException)}

# The stdlib bases PyCSL has a dedicated model for (enum #339.., NamedTuple #348, Protocol/Generic
# typing shims, ABC).  Everything else imported is "outside".
MODELLED_STD_BASES = {"Enum", "IntEnum", "Flag", "IntFlag", "StrEnum", "NamedTuple", "Protocol",
                      "Generic", "ABC", "TypedDict", "object"}
CLASS_DECO_OK = {"dataclass", "dataclasses.dataclass", "mutable_state"}
DC_KW_OK = {"frozen", "eq", "order", "init", "repr", "unsafe_hash", "kw_only", "slots", "match_args"}
METH_DECO_OK = {"staticmethod", "classmethod", "property", "abstractmethod", "abc.abstractmethod",
                "overload", "typing.overload", "override", "typing.override", "contextmanager",
                "contextlib.contextmanager", "_contextmanager", "cached_property", "functools.cached_property",
                "lru_cache", "functools.lru_cache", "mutable_state"}
# class-machinery hooks: CPython calls them implicitly; the PyCSL model never does
HOOK_DUNDERS = {"__new__", "__init_subclass__", "__class_getitem__", "__set_name__", "__get__", "__set__",
                "__delete__", "__getattr__", "__getattribute__", "__setattr__", "__delattr__",
                "__instancecheck__", "__subclasscheck__", "__prepare__", "__mro_entries__", "__del__",
                "__missing__", "__call__"}
# dunders PyCSL lowers (operator / protocol model). Anything else is unrecognised.
MODELLED_DUNDERS = {"__init__", "__post_init__", "__repr__", "__str__", "__eq__", "__ne__", "__hash__",
                    "__lt__", "__le__", "__gt__", "__ge__", "__len__", "__contains__", "__getitem__",
                    "__setitem__", "__bool__", "__add__", "__sub__", "__mul__", "__neg__", "__iter__",
                    "__next__", "__enter__", "__exit__", "__floordiv__", "__mod__", "__truediv__",
                    "__radd__", "__rsub__", "__rmul__", "__abs__", "__int__", "__index__", "__format__",
                    "__delitem__", "__and__", "__or__", "__xor__", "__invert__", "__pos__", "__pow__",
                    "__lshift__", "__rshift__", "__iadd__", "__isub__", "__imul__", "__float__"}
REFLECT_CALLS = {"setattr", "getattr", "delattr", "hasattr", "vars", "__import__"}
REFLECT_ATTRS = {"__dict__", "__class__", "__mro__", "__bases__", "__slots__", "__setattr__",
                 "__getattribute__", "__init_subclass__", "__members__", "__wrapped__"}


def dotted(e):
    if isinstance(e, ast.Name): return e.id
    if isinstance(e, ast.Attribute):
        b = dotted(e.value)
        return b + "." + e.attr if b else None
    return None


def simple_value(v):
    """class-body binding value that the model reads by value: a literal (incl. +-literal, tuple/list
    of literals), a plain name, or a dataclass field(...) call."""
    if v is None: return True
    if isinstance(v, ast.Constant): return True
    if isinstance(v, ast.UnaryOp) and isinstance(v.operand, ast.Constant): return True
    if isinstance(v, (ast.Tuple, ast.List)) and all(simple_value(x) for x in v.elts): return True
    if isinstance(v, ast.Name): return True
    if isinstance(v, ast.Attribute) and dotted(v): return True
    if isinstance(v, ast.Call) and dotted(v.func) in ("field", "dataclasses.field"): return True
    return False


STDLIB = set(getattr(sys, "stdlib_module_names", ())) | {"typing_extensions"}
# outside bases with a dedicated PyCSL model (the BASE-MODEL table of rule RA)
BASE_MODEL = {("enum", n) for n in ("Enum", "IntEnum", "Flag", "IntFlag", "StrEnum")} | \
             {("typing", n) for n in ("NamedTuple", "Protocol", "Generic", "TypedDict")} | \
             {("typing_extensions", n) for n in ("Protocol", "TypedDict")} | \
             {("abc", "ABC"), ("ast", "NodeVisitor"), ("ast", "NodeTransformer"), ("builtins", "object"),
              ("builtins", "type")}


def import_table(tree):
    """local name -> (module, attr or None)"""
    t = {}
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names:
                t[a.asname or a.name.split(".")[0]] = (a.name if a.asname else a.name.split(".")[0], None)
        elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
            for a in n.names:
                t[a.asname or a.name] = (n.module, a.name)
    return t


def classify_base(d, fcls, imps):
    """-> ('file'|'user'|'model'|'exc'|'outside'|'computed', qualified)"""
    if d is None: return ("computed", None)
    if d in fcls: return ("file", d)
    parts = d.split(".")
    if parts[0] in imps:
        mod, attr = imps[parts[0]]
        if attr is None: q = (".".join([mod] + parts[1:-1]), parts[-1]) if len(parts) > 1 else (mod, None)
        else: q = (mod, ".".join([attr] + parts[1:]))
        root = q[0].split(".")[0]
        if root not in STDLIB: return ("user", q)
        if q in BASE_MODEL: return ("model", q)
        if q[0] == "builtins" and q[1] in BUILTIN_EXC: return ("exc", q)
        return ("outside", q)
    if len(parts) == 1:
        if d in BUILTIN_EXC: return ("exc", ("builtins", d))
        if ("builtins", d) in BASE_MODEL: return ("model", ("builtins", d))
        if hasattr(_b, d): return ("outside", ("builtins", d))
    return ("unresolved", d)


def file_classes(tree):
    return {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}


def is_main_guard(n):
    t = getattr(n, "test", None)
    return (isinstance(n, ast.If) and isinstance(t, ast.Compare) and isinstance(t.left, ast.Name)
            and t.left.id == "__name__")


def strip_main(tree):
    tree.body = [n for n in tree.body if not is_main_guard(n)]
    return tree


def referenced_names(tree):
    """names loaded anywhere (outside the __main__ guard), excluding a class's own header"""
    return {n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)}


def rule_sites(tree):
    """yield (rule, line, why)"""
    tree = strip_main(tree)
    fcls = file_classes(tree)
    refs = referenced_names(tree)
    imps = import_table(tree)
    for c in ast.walk(tree):
        if not isinstance(c, ast.ClassDef): continue
        # R1 bases
        for b in c.bases:
            head = b.value if isinstance(b, ast.Subscript) else b
            d = dotted(head)
            tail = d.rsplit(".", 1)[-1] if d else None
            kind, q = classify_base(d, fcls, imps)
            if kind == "outside":
                enum_mixin = (q[0] == "builtins" and q[1] in ("int", "str") and any(
                    classify_base(dotted(x), fcls, imps)[1] in {("enum", e) for e in ("Enum", "IntEnum", "Flag", "IntFlag", "StrEnum")}
                    for x in c.bases if dotted(x)))
                if not enum_mixin:
                    yield ("RA", b.lineno, f"class {c.name}: outside base {q}")
                    if c.name in refs:
                        yield ("RAr", b.lineno, f"class {c.name} (referenced): outside base {q}")
            if kind == "model" and q[1] in ("NamedTuple", "Protocol", "TypedDict", "ABC"):
                yield ("RAm", b.lineno, f"class {c.name}: typing-construct base {q}")
            if d is None:
                yield ("R1", b.lineno, f"class {c.name}: computed base")
            elif d in fcls:
                pass
            elif d in BUILTIN_EXC or d == "object":
                pass
            elif tail in MODELLED_STD_BASES:
                if "." in d: yield ("R1a", b.lineno, f"class {c.name}: dotted base {d}")
                yield ("R1s", b.lineno, f"class {c.name}: modelled stdlib base {d}")
            else:
                yield ("R1", b.lineno, f"class {c.name}: base {d} not a file class / modelled base")
        # R2 class keywords
        for k in c.keywords:
            if k.arg == "total" and isinstance(k.value, ast.Constant): continue
            yield ("R2", c.lineno, f"class {c.name}: keyword {k.arg}=")
        # R3 class decorators
        for d in c.decorator_list:
            f = d.func if isinstance(d, ast.Call) else d
            nm = dotted(f)
            if nm not in CLASS_DECO_OK:
                yield ("R3", d.lineno, f"class {c.name}: decorator {nm or ast.unparse(d)}")
            elif isinstance(d, ast.Call):
                if d.args or any(k.arg not in DC_KW_OK or not isinstance(k.value, ast.Constant) for k in d.keywords):
                    yield ("R3", d.lineno, f"class {c.name}: dataclass(...) non-literal / unknown option")
        # R5 class-body statements, R4 method decorators, R6 dunders, R7 dunder/sunder attrs
        for s in c.body:
            if isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant):
                continue
            if isinstance(s, ast.Pass):
                continue
            if isinstance(s, ast.FunctionDef):
                for d in s.decorator_list:
                    nm = dotted(d)
                    if nm in METH_DECO_OK: continue
                    if nm and nm.endswith((".setter", ".getter", ".deleter")): continue
                    yield ("R4", d.lineno, f"{c.name}.{s.name}: decorator {nm or ast.unparse(d)}")
                n = s.name
                if n.startswith("__") and n.endswith("__"):
                    if n in HOOK_DUNDERS:
                        yield ("R6h", s.lineno, f"{c.name}.{n}: class-machinery hook")
                    if n not in MODELLED_DUNDERS:
                        yield ("R6", s.lineno, f"{c.name}.{n}: unmodelled dunder")
                continue
            if isinstance(s, ast.AsyncFunctionDef):
                yield ("R5", s.lineno, f"{c.name}: async def in class body"); continue
            if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name):
                if not simple_value(s.value):
                    yield ("R5v", s.lineno, f"{c.name}.{s.target.id}: computed annotated default")
                n = s.target.id
                if n.startswith("_") and n.endswith("_"):
                    yield ("R7", s.lineno, f"{c.name}.{n}: dunder/sunder class attribute")
                continue
            if isinstance(s, ast.Assign) and all(isinstance(t, ast.Name) for t in s.targets):
                for t in s.targets:
                    n = t.id
                    if n.startswith("_") and n.endswith("_"):
                        yield ("R7", s.lineno, f"{c.name}.{n}: dunder/sunder class attribute")
                if not simple_value(s.value):
                    yield ("R5v", s.lineno, f"{c.name}: computed class-attribute value")
                continue
            if isinstance(s, ast.ClassDef):
                yield ("R5c", s.lineno, f"{c.name}: nested class {s.name}"); continue
            if isinstance(s, ast.If) and isinstance(s.test, ast.Constant) and s.test.value is True:
                continue  # route #387's admitted `if True:` body
            yield ("R5", s.lineno, f"{c.name}: class-body statement {type(s).__name__}")
    # R8 reflection
    for n in ast.walk(tree):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id in REFLECT_CALLS:
            yield ("R8", n.lineno, f"reflection call {n.func.id}()")
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "super" and n.args:
            yield ("R8", n.lineno, "super(X, obj)")
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "type" and len(n.args) == 3:
            yield ("R8", n.lineno, "type(name, bases, ns)")
        if isinstance(n, ast.Attribute) and n.attr in REFLECT_ATTRS:
            yield ("R8", n.lineno, f"reflective attribute .{n.attr}")


def analyse(path):
    try:
        src = open(path, encoding="utf-8").read()
        tree = ast.parse(src)
    except Exception as ex:  # unparsable: pycsl refuses it anyway
        return None
    out = {}
    for r, ln, why in rule_sites(tree):
        out.setdefault(r, []).append((ln, why))
    return out


if __name__ == "__main__":
    args = sys.argv[1:]
    for p in args:
        res = analyse(p)
        if res is None:
            print(f"{p}\tPARSE-ERROR\t0\t"); continue
        if not res:
            print(f"{p}\t-\t0\t"); continue
        for r in sorted(res):
            print(f"{p}\t{r}\t{len(res[r])}\t{res[r][0][0]}: {res[r][0][1]}")
