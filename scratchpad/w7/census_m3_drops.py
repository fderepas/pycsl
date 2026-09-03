"""Census: a parsed `#@` directive that lands on an anchor whose Module-3 attachment
site IGNORES it — silently, while the run still prints 'All contracts formally proven'."""
import sys, os, importlib, collections
sys.path.insert(0, "src/pycsl")
M1 = importlib.import_module('frontend.Module1_Ingestor')
P  = importlib.import_module('frontend.Module2_Parser')
M2 = P.Module2_Parser

# consumed by a GLOBAL pass, wherever they appear
ANYWHERE = (P.DatatypeDecl, P.InductiveDecl, P.SharedDecl, P.MutexInvariant,
            P.LockOrder, P.HappyProperty)
# statement-level: attached by _attach_labels_and_ghost_assigns to ANY ast.stmt by
# lineno, but only LOWERED when that stmt has a _PY_STMT_HANDLERS entry.
STMT_LVL = (P.Label, P.CheckPoint, P.GhostAssignDecl, P.GhostArraySetDecl)

FUNC = (P.Requires, P.Ensures, P.Assigns, P.FunctionVariant, P.Diverges, P.NoInline,
        P.SiblingConcrete, P.VerifyModule, P.PropagateFrame, P.FreshGlobals, P.Trusted,
        P.Abstract, P.Lemma, P.Uses, P.InterfaceClause, P.Reveal, P.Preserves,
        P.Footprint, P.RaisesDecl, P.NoExceptionDecl, P.BoundedIntDecl, P.ProofDecl,
        P.ThreadEntry, P.Act, P.ForExpand, P.Complete, P.Disjoint,
        P.MixinDecl, P.ProvidesDecl, P.SharedStateDecl, P.TouchesFieldDecl,
        P.MethodDependencyDecl, P.ComposeFromDecl, P.ConformsToDecl)
ACCEPT = {
    "FunctionDef": FUNC,
    "ClassDef": (P.ClassInvariant, P.AllowFinalizerDecl, P.MixinDecl,
                 P.ComposeFromDecl, P.ConformsToDecl),
    "While": (P.LoopInvariant, P.LoopVariant) + STMT_LVL,
    "For":   (P.LoopInvariant, P.LoopVariant, P.AllowIterationMutationDecl) + STMT_LVL,
    "With":  (P.CriticalSection, P.Acquires, P.Releases) + STMT_LVL,
    "SimpleStatement": STMT_LVL,
    "TrailingSimpleStatement": STMT_LVL,
    "Module": (),
}
hits = collections.Counter(); detail = collections.defaultdict(list)
ROOTS = ["test-suite/corpus", "src/self-annotate", "src/pycsl_lib", "src/pycsl"]
for root in ROOTS:
    hits.clear(); detail.clear(); files = 0
    for dirpath, dirs, fns in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ("__pycache__", ".git", "attic")]
        for fn in fns:
            if not fn.endswith(".py"): continue
            p = os.path.join(dirpath, fn)
            try:
                src = open(p, encoding="utf-8", errors="replace").read()
                data = M1.Module1_Ingestor(src).process()
            except Exception:
                continue
            files += 1
            parser = M2()
            for d in data:
                try:
                    nodes = parser.parse_node_contracts(d.contracts, d.line_number)
                except Exception:
                    continue
                ok = ACCEPT.get(d.node_type, ())
                for n in nodes:
                    if isinstance(n, ANYWHERE): continue
                    if isinstance(n, ok): continue
                    k = "%s on %s" % (type(n).__name__, d.node_type)
                    hits[k] += 1
                    detail[k].append("%s:%d" % (p, d.line_number))
                    if len(detail[k]) <= 8: pass
    print("== %s (%d files) ==" % (root, files))
    if not hits: print("   (none)")
    for k, v in sorted(hits.items(), key=lambda kv: -kv[1]):
        print("   %4d  %-45s e.g. %s" % (v, k, detail[k][0]))
