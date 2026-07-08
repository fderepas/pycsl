#!/usr/bin/env python3
"""Phase 3.0 census refinement: classify \\trusted collection-result builders by LIVE body.

Full pool = trusted methods (9 IR-consuming modules) whose LIVE body's OUTPUT is a
collection: a returned local set/list/dict, a by-ref mutated param collection, or a
returned comprehension. Classify each by result type + clean|complicated.

Script PRE-FILTERS; the human confirms CLEAN by reading each live body.
"""
import ast
import re
import json
from pathlib import Path
from collections import Counter, defaultdict

ROOT = Path("/home/fabrice.derepas@canonical.com/git/pycsl")
MIRROR = ROOT / "src/self-annotate/src"
LIVE = ROOT / "src/pycsl"

MODULES = [
    "core_ir_semantic.py", "Module6_WhyMLTranspiler.py",
    "frontend/Module5_IREmitter.py", "frontend/ir_resolve.py",
    "frontend/ir_inline.py", "frontend/monomorphize.py",
    "frontend/module_collect.py", "frontend/exec_splice.py",
]
for p in sorted((MIRROR / "module6_whyml").glob("*.py")):
    MODULES.append("module6_whyml/" + p.name)

TYPING_NAMES = {"Set", "List", "Dict", "Tuple", "Optional", "Union", "Any",
                "FrozenSet", "Sequence", "Mapping", "MutableMapping", "Iterable",
                "Iterator", "Callable", "Type", "DefaultDict", "Deque", "Counter"}
BUILTIN_OK = {"set", "list", "dict", "isinstance", "len", "int", "str", "bool",
              "any", "all", "sorted", "enumerate", "range", "tuple", "frozenset",
              "items", "values", "keys", "get", "add", "append", "update", "extend",
              "sort", "reversed", "min", "max", "abs", "repr", "type",
              # str methods (benign, not sibling helpers)
              "rsplit", "split", "startswith", "endswith", "strip", "lstrip",
              "rstrip", "join", "replace", "lower", "upper", "format", "count",
              "index", "find", "splitlines", "encode", "decode", "title",
              "capitalize", "zfill", "ljust", "rjust", "removeprefix", "removesuffix",
              # dict/set/list read/copy methods
              "copy", "setdefault", "discard", "remove", "pop", "clear",
              "issubset", "issuperset", "union", "intersection", "difference"}


def trusted_methods(mf: Path):
    if not mf.exists():
        return set()
    L = mf.read_text().splitlines()
    T = set()
    for i, ln in enumerate(L):
        m = re.match(r"\s*def\s+(\w+)\s*\(", ln)
        if not m:
            continue
        j = i - 1
        st = False
        while j >= 0:
            s = L[j].strip()
            if s.startswith(("@", "#")) or s == "":
                if "\\trusted" in s:
                    st = True
                j -= 1
                continue
            break
        if st:
            T.add(m.group(1))
    return T


def is_lit_str(n):
    return isinstance(n, ast.Constant) and isinstance(n.value, str)


def callname(func):
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return None


class BF:
    def __init__(self, fn, params):
        self.fn = fn
        self.name = fn.name
        self.params = params
        self.loc = (fn.end_lineno or fn.lineno) - fn.lineno + 1
        self.run()

    def run(self):
        fn = self.fn
        selfname = self.name
        # local collection inits
        self.local_kind = {}   # var -> kind from init
        for nd in ast.walk(fn):
            if isinstance(nd, ast.Assign) and len(nd.targets) == 1 and isinstance(nd.targets[0], ast.Name):
                k = self._collkind(nd.value)
                if k:
                    self.local_kind[nd.targets[0].id] = k
        # mutation ops per var
        self.mut_kind = defaultdict(set)   # var -> set of inferred kinds
        self.self_recursive = False
        self.calls_other = set()
        self.in_loop_return = False
        self.in_loop_break = False
        self.has_var_get = False
        self.has_var_subscript = False
        self.subject_mutation_vars = set()
        self.returns_bool_lit = False
        self.has_any_all = False
        self.num_returns = 0
        self.returned_names = set()
        self.returns_comp = None   # 'list'|'set'|'dict'
        self.returns_join = False
        self.subject_names = set()     # names isinstance-tested as dict/list
        self.setitem_vars = set()      # names written via NAME[k] = ...
        self.mutating_call_vars = set()  # names .add/.append/.update/.pop-ed
        self.var_read_bases = set()      # names read via NAME[var] in Load ctx

        for nd in ast.walk(fn):
            # isinstance(x, dict/list) -> subject
            if isinstance(nd, ast.Call) and callname(nd.func) == "isinstance" and len(nd.args) == 2:
                if isinstance(nd.args[0], ast.Name):
                    tgt = nd.args[1]
                    names = []
                    if isinstance(tgt, ast.Name):
                        names = [tgt.id]
                    elif isinstance(tgt, ast.Tuple):
                        names = [e.id for e in tgt.elts if isinstance(e, ast.Name)]
                    if any(n in ("dict", "list") for n in names):
                        self.subject_names.add(nd.args[0].id)
            if isinstance(nd, ast.AugAssign) and isinstance(nd.target, ast.Name):
                if isinstance(nd.op, ast.BitOr):
                    self.mut_kind[nd.target.id].add("set")
                elif isinstance(nd.op, ast.Add):
                    self.mut_kind[nd.target.id].add("list")
            if isinstance(nd, ast.Assign):
                for t in nd.targets:
                    if isinstance(t, ast.Subscript) and isinstance(t.value, ast.Name):
                        self.mut_kind[t.value.id].add("dict")
                        self.setitem_vars.add(t.value.id)
            if isinstance(nd, ast.Call):
                f = nd.func
                if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
                    bn = f.value.id
                    if f.attr == "add":
                        self.mut_kind[bn].add("set")
                        self.mutating_call_vars.add(bn)
                    elif f.attr in ("append", "extend", "insert"):
                        self.mut_kind[bn].add("list")
                        self.mutating_call_vars.add(bn)
                    elif f.attr == "update":
                        self.mut_kind[bn].add("dict")
                        self.mutating_call_vars.add(bn)
                    elif f.attr == "pop":
                        self.subject_mutation_vars.add(bn)
                    if f.attr == "get" and nd.args and not is_lit_str(nd.args[0]):
                        self.has_var_get = True
                cn = callname(f)
                if cn == selfname:
                    self.self_recursive = True
                elif cn and cn not in BUILTIN_OK:
                    self.calls_other.add(cn)
            # variable-key subscript READ of a subject (Load ctx, NAME[var]).
            # Exclude typing-generic annotations (Set[str], List[int], ...).
            if isinstance(nd, ast.Subscript) and isinstance(nd.value, ast.Name):
                if (isinstance(getattr(nd, "ctx", None), ast.Load)
                        and isinstance(nd.slice, ast.Name)
                        and nd.value.id not in TYPING_NAMES):
                    self.var_read_bases.add(nd.value.id)
            if isinstance(nd, ast.Delete):
                for tg in nd.targets:
                    if isinstance(tg, ast.Subscript) and isinstance(tg.value, ast.Name):
                        self.subject_mutation_vars.add(tg.value.id)
            if isinstance(nd, ast.Return):
                self.num_returns += 1
                v = nd.value
                if isinstance(v, ast.Name):
                    self.returned_names.add(v.id)
                if isinstance(v, ast.Constant) and isinstance(v.value, bool):
                    self.returns_bool_lit = True
                if isinstance(v, ast.Call) and callname(v.func) in ("any", "all"):
                    self.has_any_all = True
                if isinstance(v, ast.ListComp):
                    self.returns_comp = "list"
                if isinstance(v, ast.SetComp):
                    self.returns_comp = "set"
                if isinstance(v, ast.DictComp):
                    self.returns_comp = "dict"
                if isinstance(v, ast.JoinedStr):
                    self.returns_join = True

        # in-loop return/break
        for nd in ast.walk(fn):
            if isinstance(nd, (ast.For, ast.While)):
                for s in ast.walk(nd):
                    if isinstance(s, ast.Return):
                        self.in_loop_return = True
                    if isinstance(s, ast.Break):
                        self.in_loop_break = True

        self._pick_accumulator()

    def _collkind(self, v):
        if isinstance(v, ast.Call):
            n = callname(v.func)
            if n in ("set", "frozenset"):
                return "set"
            if n == "list":
                return "list"
            if n == "dict":
                return "dict"
        if isinstance(v, ast.Set):
            return "set"
        if isinstance(v, ast.List):
            return "list"
        if isinstance(v, ast.Dict):
            return "dict"
        return None

    def _pick_accumulator(self):
        # Priority: returned local collection -> by-ref mutated param -> comprehension return
        self.acc_var = None
        self.acc_kind = None
        self.acc_mode = None  # 'return-local' | 'by-ref-param' | 'comprehension'
        # returned local collection
        for v in self.returned_names:
            if v in self.local_kind:
                self.acc_var = v
                self.acc_kind = self.local_kind[v]
                self.acc_mode = "return-local"
                return
            if v in self.mut_kind:
                self.acc_var = v
                self.acc_kind = sorted(self.mut_kind[v])[0]
                self.acc_mode = "return-local"
                return
        # by-ref param accumulator: a param that is mutated
        for p in self.params:
            if p in self.mut_kind:
                self.acc_var = p
                self.acc_kind = sorted(self.mut_kind[p])[0]
                self.acc_mode = "by-ref-param"
                return
        # comprehension
        if self.returns_comp:
            self.acc_kind = self.returns_comp
            self.acc_mode = "comprehension"
            return

    def family(self):
        if self.acc_kind == "set":
            return "A-set"
        if self.acc_kind == "list":
            return "A-list"
        if self.acc_kind == "dict":
            return "A-dict"
        if self.has_any_all or (self.returns_bool_lit and self.self_recursive):
            return "A-bool"
        return "other"

    def is_builder(self):
        return self.acc_kind in ("set", "list", "dict")

    def clean(self):
        r = []
        acc = self.acc_var
        if self.acc_mode == "comprehension":
            r.append("comprehension-not-fold")
        if not self.self_recursive:
            r.append("no-self-recursion")
        if self.calls_other:
            r.append("sibling-call:" + ",".join(sorted(self.calls_other)[:3]))
        if self.in_loop_return:
            r.append("in-loop-return")
        if self.in_loop_break:
            r.append("in-loop-break")
        if self.has_var_get:
            r.append("variable-key-get")
        # variable-key subscript READ of a name other than the accumulator (subject read)
        vr = self.var_read_bases - ({acc} if acc else set())
        if vr:
            r.append("variable-subscript-read")
        # in-place subject mutation: accumulator IS the walked subject, OR
        # a mutating write/call/del targets a subject name (not the accumulator)
        if acc and acc in self.subject_names:
            r.append("subject-mutation(acc==subject)")
        mut_on_subject = (self.setitem_vars | self.mutating_call_vars |
                          self.subject_mutation_vars) & self.subject_names
        mut_on_subject -= ({acc} if acc else set())
        if mut_on_subject:
            r.append("subject-mutation")
        sm = self.subject_mutation_vars - ({acc} if acc else set())
        if sm and "subject-mutation" not in r:
            r.append("subject-mutation")
        if not self.is_builder():
            r.append("not-collection-builder")
        return (len(r) == 0), (";".join(r) if r else "CLEAN")


def live_fns(lf: Path):
    if not lf.exists():
        return {}
    tree = ast.parse(lf.read_text())
    out = {}
    for nd in ast.walk(tree):
        if isinstance(nd, (ast.FunctionDef, ast.AsyncFunctionDef)):
            params = [a.arg for a in nd.args.args] + [a.arg for a in nd.args.posonlyargs]
            out[nd.name] = (nd, params)
    return out


rows = []
for mod in MODULES:
    T = trusted_methods(MIRROR / mod)
    fns = live_fns(LIVE / mod)
    for name in sorted(T):
        got = fns.get(name)
        if got is None:
            rows.append({"file": mod, "name": name, "family": "NO-LIVE-BODY",
                         "builder": False, "clean": False, "reason": "no-live-body",
                         "loc": 0, "mode": None})
            continue
        fn, params = got
        bf = BF(fn, params)
        cl, reason = bf.clean()
        rows.append({
            "file": mod, "name": name, "family": bf.family(),
            "builder": bf.is_builder(), "clean": cl, "reason": reason,
            "loc": bf.loc, "mode": bf.acc_mode, "kind": bf.acc_kind,
            "self_rec": bf.self_recursive, "acc_var": bf.acc_var,
        })

(ROOT / "scratchpad/phase3_census_rows.json").write_text(json.dumps(rows, indent=1))

tot = len(rows)
builders = [r for r in rows if r["builder"]]
bools = [r for r in rows if r["family"] == "A-bool"]
print(f"Total trusted (9 IR modules, live body found): {sum(1 for r in rows if r['family']!='NO-LIVE-BODY')}")
print(f"NO-LIVE-BODY (renamed/absent): {sum(1 for r in rows if r['family']=='NO-LIVE-BODY')}")
print(f"Collection builders (set/list/dict output): {len(builders)}")
print(f"A-bool predicates: {len(bools)}")
print()
by = defaultdict(lambda: {"total": 0, "clean": 0, "cx": 0, "reasons": Counter(), "modes": Counter()})
for r in builders:
    d = by[r["family"]]
    d["total"] += 1
    d["modes"][r["mode"]] += 1
    if r["clean"]:
        d["clean"] += 1
    else:
        d["cx"] += 1
        for rr in r["reason"].split(";"):
            d["reasons"][rr.split(":")[0]] += 1
print("=== BUILDERS by family ===")
for f in ("A-set", "A-list", "A-dict"):
    d = by[f]
    print(f"\n{f}: total={d['total']} CLEAN={d['clean']} complicated={d['cx']}")
    print("   modes:", dict(d["modes"]))
    print("   top reasons:", dict(d["reasons"].most_common(7)))
print("\n=== CLEAN candidates (pre-filter) ===")
for r in builders:
    if r["clean"]:
        print(f"  [{r['family']}/{r['mode']}] {r['file']}::{r['name']} ({r['loc']}L) acc={r['acc_var']}")
