"""lib_param_write_closure — which PARAMETERS may a live function write? (route #401)

Used by `check-trusted-frame-honesty.py`'s PARAMETER-WRITE arm. The SELF arm of that plane
computes `self.<f>` stores and propagates them along the call graph; a write THROUGH A
PARAMETER (`p[:] = v`, `p.x = v`, `del p.x`, `setattr(p, ...)`, `delattr(p, ...)`,
`p.append(...)` and the other in-place mutators, or forwarding `p` to a callee whose own
closure writes that position) is outside its population. Route #401 is the carrier:
`pure_ast.NodeTransformer.generic_visit` is `\trusted` with `#@ assigns \nothing` while its
live body rewrites `node` IN PLACE (`old_value[:] = new_values`, `delattr`, `setattr`).

THE ANALYSIS, and where it is approximate (stated so nobody reads more into a number than
is there):
  * ALIASES are FLOW-SENSITIVE per function (`x = dict(x)` rebinding to a fresh copy KILLS
    the alias; branches JOIN by union). An alias is `obj` (the parameter or an object
    reachable from it: attribute / item reads, `getattr(p, ...)`, `.get(...)`, iteration
    elements) or `view` (a fresh container whose ELEMENTS are reachable: `list(p)`,
    `p[a:b]`, `iter_fields(p)`, `p.items()`, ...). A store into an `obj` alias writes the
    parameter; a store into a `view` does not, a store into an ELEMENT of a view does.
    The frame is therefore DEEP: `assigns p` covers everything reachable from `p`.
  * CALLS resolve per RECEIVER CLASS CONTEXT: `self.m()` / `super().m()` / the
    `getattr(self, 'visit_' + ..., self.generic_visit)` dispatch idiom are looked up in the
    MRO of each concrete receiver class `R` the method can run on (its own class and every
    subclass), so `NodeVisitor.visit` running on a `NodeTransformer` subclass reaches
    `generic_visit`'s in-place rewrite while `_Unparser`'s own `visit_*` do not leak into an
    unrelated `NodeVisitor` subclass. `Cls(...).m()` runs under context `Cls`; `mod.f()` /
    `from mod import f` resolve by module STEM; bare `f()` within the same file.
  * UNDER-approximations: an alias stored into a container and read back later, a
    callee reached through a value the analysis cannot name (a callback, a bound method
    stored in a field), `+=` on a parameter not annotated as a list/dict/set, and
    per-key flow (`d = dict(p); d["k"] = p["k"]; d["k"]["x"] = 1` is seen as a write
    to `p`, an OVER-approximation, while a field replaced by a fresh value and then
    written is also reported). The number it yields is a census, not a theorem.
"""
import ast, collections, os, sys

MUT = frozenset({"append", "extend", "insert", "add", "update", "pop", "popitem", "clear",
                 "remove", "discard", "setdefault", "sort", "reverse",
                 "difference_update", "intersection_update", "symmetric_difference_update"})
COPY_CALLS = frozenset({"list", "tuple", "set", "frozenset", "sorted", "dict",
                        "iter_fields", "iter_child_nodes", "walk", "enumerate",
                        "reversed", "zip", "iter", "filter", "map"})
VIEW_METHODS = frozenset({"items", "values", "keys", "copy"})
OBJ_METHODS = frozenset({"get", "setdefault"})


def parse(root):
    funcs, classes, bases, imports = {}, {}, collections.defaultdict(list), {}
    for dp, _d, fs in os.walk(root):
        if "__pycache__" in dp:
            continue
        for fn in sorted(fs):
            if not fn.endswith(".py"):
                continue
            p = os.path.join(dp, fn)
            try:
                t = ast.parse(open(p).read())
            except (OSError, SyntaxError):
                continue
            imp = {}
            for n in ast.walk(t):
                if isinstance(n, ast.Import):
                    for a in n.names:
                        imp[a.asname or a.name.split(".")[0]] = ("mod", a.name.split(".")[-1])
                elif isinstance(n, ast.ImportFrom):
                    for a in n.names:
                        imp[a.asname or a.name] = ("from", (n.module or "").split(".")[-1], a.name)
            imports[p] = imp
            for node in t.body:
                if isinstance(node, ast.FunctionDef):
                    funcs[(p, "", node.name)] = node
                elif isinstance(node, ast.ClassDef):
                    classes.setdefault(node.name, p)
                    for b in node.bases:
                        nm = b.id if isinstance(b, ast.Name) else b.attr if isinstance(b, ast.Attribute) else None
                        if nm and nm not in bases[node.name]:
                            bases[node.name].append(nm)
                    for m in node.body:
                        if isinstance(m, ast.FunctionDef):
                            funcs[(p, node.name, m.name)] = m
    stem = collections.defaultdict(set)
    for (p, c, n) in funcs:
        stem[os.path.basename(p)[:-3]].add(p)
    return funcs, classes, bases, imports, {k: sorted(v) for k, v in stem.items()}


def mro(c, bases):
    out, todo = [], [c]
    while todo:
        x = todo.pop(0)
        if x in out:
            continue
        out.append(x)
        todo.extend(bases.get(x, []))
    return out


def params_of(fn, is_method):
    a = fn.args
    ps = [x.arg for x in a.posonlyargs + a.args]
    static = any(isinstance(d, ast.Name) and d.id == "staticmethod" for d in fn.decorator_list)
    if is_method and ps and not static:
        ps = ps[1:]
    return ps, [x.arg for x in a.kwonlyargs] + ([a.vararg.arg] if a.vararg else [])


def join(a, b):
    out = {k: dict(v) for k, v in a.items()}
    for n, d in b.items():
        cur = out.setdefault(n, {})
        for p, k in d.items():
            cur[p] = "obj" if "obj" in (k, cur.get(p)) else k
    return out


class FnAnalysis:
    def __init__(self, fn, params, imports, classes, stem):
        self.fn, self.params = fn, params
        self.imports, self.classes, self.stem = imports, classes, stem
        self.direct = collections.defaultdict(list)
        self.sites = []
        self.dyn = {}

    def ekind(self, e, st):
        if isinstance(e, ast.Name):
            return dict(st.get(e.id, {}))
        if isinstance(e, ast.Attribute):
            return {p: "obj" for p in self.ekind(e.value, st)}
        if isinstance(e, ast.Subscript):
            k = "view" if isinstance(e.slice, ast.Slice) else "obj"
            return {p: k for p in self.ekind(e.value, st)}
        if isinstance(e, ast.Starred):
            return self.ekind(e.value, st)
        if isinstance(e, ast.NamedExpr):
            d = self.ekind(e.value, st)
            self.bind(e.target, d, st)
            return d
        if isinstance(e, ast.IfExp):
            d = self.ekind(e.body, st)
            d.update(self.ekind(e.orelse, st))
            return d
        if isinstance(e, ast.BoolOp):
            d = {}
            for v in e.values:
                d.update(self.ekind(v, st))
            return d
        if isinstance(e, ast.Call):
            f = e.func
            fname = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else None
            if isinstance(f, ast.Name) and fname == "getattr" and e.args:
                return {p: "obj" for p in self.ekind(e.args[0], st)}
            if fname in COPY_CALLS and (isinstance(f, ast.Name) or (
                    isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
                    and self.imports.get(f.value.id, ("",))[0] in ("mod", "from"))):
                d = {}
                for a in e.args:
                    d.update({p: "view" for p in self.ekind(a, st)})
                return d
            if isinstance(f, ast.Attribute) and f.attr in VIEW_METHODS:
                return {p: "view" for p in self.ekind(f.value, st)}
            if isinstance(f, ast.Attribute) and f.attr in OBJ_METHODS:
                return {p: "obj" for p in self.ekind(f.value, st)}
            return {}
        if isinstance(e, (ast.Tuple, ast.List, ast.Set)):
            d = {}
            for x in e.elts:
                d.update(self.ekind(x, st))
            return {p: "view" for p in d}
        return {}

    def bind(self, t, d, st):
        if isinstance(t, ast.Name):
            if d:
                st[t.id] = dict(d)
            else:
                st.pop(t.id, None)
        elif isinstance(t, (ast.Tuple, ast.List)):
            for x in t.elts:
                self.bind(x, {p: "obj" for p in d}, st)
        elif isinstance(t, ast.Starred):
            self.bind(t.value, {p: "view" for p in d}, st)

    def objp(self, e, st):
        return {p for p, k in self.ekind(e, st).items() if k == "obj"}

    def scan_expr(self, e, st):
        """Record writes / call sites inside an expression evaluated in state `st`."""
        if e is None:
            return
        for n in self._walk_expr(e, st):
            pass

    def _walk_expr(self, e, st):
        # manual walk so comprehensions bind their targets in a local copy
        stack = [(e, st)]
        while stack:
            n, s = stack.pop()
            if isinstance(n, (ast.ListComp, ast.SetComp, ast.GeneratorExp, ast.DictComp)):
                s2 = {k: dict(v) for k, v in s.items()}
                for g in n.generators:
                    stack.append((g.iter, s2))
                    self.bind(g.target, {p: "obj" for p in self.ekind(g.iter, s2)}, s2)
                    for c in g.ifs:
                        stack.append((c, s2))
                if isinstance(n, ast.DictComp):
                    stack.append((n.key, s2)); stack.append((n.value, s2))
                else:
                    stack.append((n.elt, s2))
                continue
            if isinstance(n, ast.Lambda):
                stack.append((n.body, s))
                continue
            if isinstance(n, ast.NamedExpr):
                self.bind(n.target, self.ekind(n.value, s), s)
            if isinstance(n, ast.Call):
                self.call(n, s)
            for c in ast.iter_child_nodes(n):
                if isinstance(c, ast.expr):
                    stack.append((c, s))
                elif isinstance(c, ast.keyword):
                    stack.append((c.value, s))
            yield n

    def call(self, n, st):
        f = n.func
        if isinstance(f, ast.Name) and f.id in ("setattr", "delattr") and n.args:
            for p in self.objp(n.args[0], st):
                self.direct[p].append("%s() L%d" % (f.id, n.lineno))
        if isinstance(f, ast.Attribute) and f.attr in MUT:
            for p in self.objp(f.value, st):
                self.direct[p].append(".%s() L%d" % (f.attr, n.lineno))
        args = [(i, self.objp(a, st)) for i, a in enumerate(n.args) if not isinstance(a, ast.Starred)]
        args += [(k.arg, self.objp(k.value, st)) for k in n.keywords if k.arg]
        args = [(i, s) for i, s in args if s]
        if not args:
            return
        site = None
        if isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name) and f.value.id == "self":
            site = ("self", f.attr)
        elif (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Call)
              and isinstance(f.value.func, ast.Name) and f.value.func.id == "super"):
            site = ("super", f.attr)
        elif (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Call)
              and isinstance(f.value.func, ast.Name) and f.value.func.id in self.classes):
            site = ("cls", f.value.func.id, f.attr)
        elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
            imp = self.imports.get(f.value.id)
            if imp and imp[0] == "mod":
                site = ("modfn", imp[1], f.attr)
            elif imp and imp[0] == "from" and imp[2] in self.stem:
                site = ("modfn", imp[2], f.attr)
            elif f.value.id in self.classes:
                site = ("cls", f.value.id, f.attr)
        elif isinstance(f, ast.Name):
            if f.id in self.dyn:
                site = ("dyn",) + self.dyn[f.id]
            elif f.id in self.imports and self.imports[f.id][0] == "from":
                site = ("modfn", self.imports[f.id][1], self.imports[f.id][2])
            else:
                site = ("local", f.id)
        if site:
            self.sites.append((site, args, n.lineno))

    def store_target(self, t, st, lineno):
        for t2 in (t.elts if isinstance(t, (ast.Tuple, ast.List)) else [t]):
            if isinstance(t2, ast.Starred):
                t2 = t2.value
            if isinstance(t2, (ast.Subscript, ast.Attribute)):
                for p in self.objp(t2.value, st):
                    self.direct[p].append("%s-store L%d" % (type(t2).__name__, lineno))
                self.scan_expr(t2.value, st)
                if isinstance(t2, ast.Subscript):
                    self.scan_expr(t2.slice, st)

    def note_dyn(self, name, v):
        if (isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and v.func.id == "getattr"
                and v.args and isinstance(v.args[0], ast.Name) and v.args[0].id == "self"):
            pref = None
            if len(v.args) > 1:
                a1 = v.args[1]
                if isinstance(a1, ast.Constant) and isinstance(a1.value, str):
                    pref = ("eq", a1.value)
                elif isinstance(a1, ast.BinOp) and isinstance(a1.left, ast.Constant):
                    pref = ("prefix", a1.left.value)
                else:
                    pref = ("prefix", self._name_prefix.get(getattr(a1, "id", None), ""))
            dflt = None
            if len(v.args) > 2 and isinstance(v.args[2], ast.Attribute) \
                    and isinstance(v.args[2].value, ast.Name) and v.args[2].value.id == "self":
                dflt = v.args[2].attr
            self.dyn[name] = (pref, dflt)

    def run(self):
        self._name_prefix = {}
        for n in ast.walk(self.fn):
            if (isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
                    and isinstance(n.value, ast.BinOp) and isinstance(n.value.left, ast.Constant)
                    and isinstance(n.value.left.value, str)):
                self._name_prefix[n.targets[0].id] = n.value.left.value
        for n in ast.walk(self.fn):
            if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                self.note_dyn(n.targets[0].id, n.value)
        self.listy = set()
        for a in self.fn.args.posonlyargs + self.fn.args.args + self.fn.args.kwonlyargs:
            ann = a.annotation
            txt = ast.unparse(ann) if ann is not None else ""
            if a.arg in self.params and txt.split("[")[0].split(".")[-1] in ("list", "List", "dict", "Dict", "set", "Set"):
                self.listy.add(a.arg)
        st = {p: {p: "obj"} for p in self.params}
        self.stmts(self.fn.body, st)

    def stmts(self, body, st):
        for s in body:
            st = self.stmt(s, st)
        return st

    def stmt(self, s, st):
        if isinstance(s, ast.Assign):
            self.scan_expr(s.value, st)
            d = self.ekind(s.value, st)
            for t in s.targets:
                self.store_target(t, st, s.lineno)
                if (isinstance(t, (ast.Tuple, ast.List)) and isinstance(s.value, (ast.Tuple, ast.List))
                        and len(t.elts) == len(s.value.elts)):
                    ds = [self.ekind(v, st) for v in s.value.elts]
                    for tt, dd in zip(t.elts, ds):
                        self.bind(tt, dd, st)
                else:
                    self.bind(t, d, st)
        elif isinstance(s, ast.AnnAssign):
            if s.value is not None:
                self.scan_expr(s.value, st)
                self.store_target(s.target, st, s.lineno)
                self.bind(s.target, self.ekind(s.value, st), st)
        elif isinstance(s, ast.AugAssign):
            self.scan_expr(s.value, st)
            self.store_target(s.target, st, s.lineno)
            if isinstance(s.target, ast.Name) and s.target.id in self.listy:
                # `xs += ys` on a LIST-annotated parameter is IN PLACE (an int `i += 1` rebinds)
                self.direct[s.target.id].append("+= L%d" % s.lineno)
        elif isinstance(s, ast.Delete):
            for t in s.targets:
                self.store_target(t, st, s.lineno)
        elif isinstance(s, (ast.Expr, ast.Return)):
            self.scan_expr(s.value, st)
        elif isinstance(s, ast.If):
            self.scan_expr(s.test, st)
            a = self.stmts(s.body, {k: dict(v) for k, v in st.items()})
            b = self.stmts(s.orelse, {k: dict(v) for k, v in st.items()})
            st = join(a, b)
        elif isinstance(s, (ast.For, ast.AsyncFor, ast.While)):
            pre = st
            for _ in range(3):
                cur = {k: dict(v) for k, v in pre.items()}
                if isinstance(s, ast.While):
                    self.scan_expr(s.test, cur)
                else:
                    self.scan_expr(s.iter, cur)
                    self.bind(s.target, {p: "obj" for p in self.ekind(s.iter, cur)}, cur)
                cur = self.stmts(s.body, cur)
                nxt = join(pre, cur)
                if nxt == pre:
                    break
                pre = nxt
            st = self.stmts(s.orelse, pre)
        elif isinstance(s, (ast.With, ast.AsyncWith)):
            for it in s.items:
                self.scan_expr(it.context_expr, st)
                if it.optional_vars is not None:
                    self.bind(it.optional_vars, self.ekind(it.context_expr, st), st)
            st = self.stmts(s.body, st)
        elif isinstance(s, (ast.Try,) + ((ast.TryStar,) if hasattr(ast, "TryStar") else ())):
            a = self.stmts(s.body, {k: dict(v) for k, v in st.items()})
            m = join(st, a)
            outs = [a]
            for h in s.handlers:
                outs.append(self.stmts(h.body, {k: dict(v) for k, v in m.items()}))
            r = st
            for o in outs:
                r = join(r, o)
            r = self.stmts(s.orelse, r)
            st = self.stmts(s.finalbody, r)
        elif isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef)):
            # a nested def runs later with the CURRENT bindings visible: analyse its body now
            inner = {k: dict(v) for k, v in st.items()}
            for a in s.args.args + s.args.kwonlyargs:
                inner.pop(a.arg, None)
            self.stmts(s.body, inner)
        elif isinstance(s, ast.Match):
            self.scan_expr(s.subject, st)
            r = st
            for c in s.cases:
                r = join(r, self.stmts(c.body, {k: dict(v) for k, v in st.items()}))
            st = r
        elif isinstance(s, (ast.Raise, ast.Assert)):
            for c in ast.iter_child_nodes(s):
                if isinstance(c, ast.expr):
                    self.scan_expr(c, st)
        return st


def analyse(root):
    funcs, classes, bases, imports, stem = parse(root)
    M = {c: mro(c, bases) for c in classes}
    desc = collections.defaultdict(set)
    for c in classes:
        for b in M[c][1:]:
            desc[b].add(c)
    defs = collections.defaultdict(dict)  # class -> name -> key
    for k in funcs:
        if k[1]:
            defs[k[1]].setdefault(k[2], k)
    info = {}
    for key, fn in funcs.items():
        ps, kws = params_of(fn, bool(key[1]))
        fa = FnAnalysis(fn, ps + kws, imports[key[0]], classes, stem)
        fa.run()
        info[key] = dict(params=ps, kws=kws, direct={p: sorted(set(v), key=v.index) for p, v in fa.direct.items()}, sites=fa.sites)

    def lookup(ctx, name, after=None):
        if ctx not in M:
            return None
        order = M[ctx]
        if after is not None:
            if after not in order:
                return None
            order = order[order.index(after) + 1:]
        for c in order:
            if name in defs.get(c, {}):
                return defs[c][name]
        return None

    def resolve(key, ctx, site):
        path, cls, _ = key
        k = site[0]
        if k == "self":
            r = lookup(ctx, site[1]) if ctx else None
            return [(r, ctx)] if r else []
        if k == "super":
            r = lookup(ctx, site[1], after=cls) if ctx else None
            return [(r, ctx)] if r else []
        if k == "cls":
            r = lookup(site[1], site[2])
            return [(r, site[1])] if r else []
        if k == "modfn":
            return [((p, "", site[2]), None) for p in stem.get(site[1], ()) if (p, "", site[2]) in funcs]
        if k == "local":
            if (path, "", site[1]) in funcs:
                return [((path, "", site[1]), None)]
            if site[1] in classes:
                r = lookup(site[1], "__init__")
                return [(r, site[1])] if r else []
            return []
        if k == "dyn":
            pref, dflt = site[1], site[2]
            out = []
            if not ctx:
                return out
            names = set()
            for c in M[ctx]:
                for nm in defs.get(c, {}):
                    if pref and ((pref[0] == "eq" and nm == pref[1]) or
                                 (pref[0] == "prefix" and nm.startswith(pref[1]))):
                        names.add(nm)
            if dflt:
                names.add(dflt)
            for nm in names:
                r = lookup(ctx, nm)
                if r:
                    out.append((r, ctx))
            return out
        return []

    # contexts: module funcs -> None; methods of class C -> every R in {C} | desc(C) with lookup(R, m) == key
    pairs = []
    for key in funcs:
        if not key[1]:
            pairs.append((key, None))
        else:
            for R in {key[1]} | desc[key[1]]:
                if lookup(R, key[2]) == key:
                    pairs.append((key, R))
    W = {pr: {p: list(v) for p, v in info[pr[0]]["direct"].items()} for pr in pairs}
    for _ in range(80):
        ch = False
        for pr in pairs:
            key, ctx = pr
            for site, args, ln in info[key]["sites"]:
                for tgt in resolve(key, ctx, site):
                    tw = W.get(tgt)
                    if tw is None:
                        tw = W[tgt] = {p: list(v) for p, v in info[tgt[0]]["direct"].items()}
                        pairs.append(tgt)
                        ch = True
                    if not tw:
                        continue
                    ti = info[tgt[0]]
                    for pos, ps in args:
                        tp = (ti["params"][pos] if isinstance(pos, int) and pos < len(ti["params"])
                              else pos if not isinstance(pos, int) else None)
                        if tp in tw:
                            for p in ps:
                                if p not in W[pr]:
                                    W[pr][p] = ["L%d via %s.%s(%s)" % (ln, tgt[0][1] or os.path.basename(tgt[0][0]), tgt[0][2], tp)]
                                    ch = True
        if not ch:
            break
    # per function: union over contexts
    U = collections.defaultdict(dict)
    for (key, ctx), w in W.items():
        for p, v in w.items():
            U[key].setdefault(p, v)
    return funcs, info, U


if __name__ == "__main__":
    _funcs, _info, _u = analyse(sys.argv[1] if len(sys.argv) > 1 else "src/pycsl")
    print("functions writing a parameter:", sum(1 for k in _u if _u[k]))
