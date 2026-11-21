#!/usr/bin/env python3
"""classify.py <chain.jsonl> : seam family per chain event (ordered regex rules over msg / stmt / snip / root_rhs)."""
import json, re, sys, collections

STRM = r"split|rsplit|splitlines|strip|lstrip|rstrip|startswith|endswith|partition|rpartition|join|replace|lower|upper|find|rfind|index|count|isidentifier|isdigit|isalpha|isalnum|isspace|isupper|islower|format|encode|decode|removeprefix|removesuffix|ljust|rjust|center|zfill|casefold|title|expandtabs"

# (family, predicate) ; predicate gets dict e with keys m s n r a
RULES = [
    ("MUTRECV in-place mutator (.pop/.add/.extend/.setdefault/.update/... on local/self-field)", lambda e: "MUTATES its receiver" in e["m"] or "appends to the collection in the field" in e["m"]),
    ("MUTRECV2", lambda e: "SLICE delete" in e["m"]),
    ("MUTPARAM in-place mutation of a dict/set/list PARAMETER (caller-visible writes frame)", lambda e: "in-place mutation of dict/set parameter" in e["m"] or "in-place `append` to list parameter" in e["m"]),
    ("ALIAS dict/set value observed through two names / mutated dict aliased or stored", lambda e: "a dict/set value reaches" in e["m"] or "aliasing a mutated dict" in e["m"] or "storing a mutated dict" in e["m"]),
    ("SIG mirror/live signature arity mismatch at a call", lambda e: re.search(r"passes \d+ positional argument", e["m"]) is not None),
    ("NESTED def lift / closure", lambda e: "nested function" in e["m"] or e["s"].startswith("NESTED def") or "nonlocal" in e["m"]),
    ("WITH-AS context manager", lambda e: "with ... as" in e["m"] or e["s"].startswith("HDR With")),
    ("EXC exception object read / except-as / try-else", lambda e: "exception object" in e["m"] or "can be reached by an exception the model does not raise" in e["m"] or "raises unlisted exception" in e["m"] or "ROUTE #233" in e["m"] or "ROUTE #175" in e["m"] or "ROUTE #37" in e["m"] or "ROUTE #179" in e["m"] or e["s"].startswith("HDR except")),
    ("REBIND name rebound / namespace-dict write / global / dynamic eval", lambda e: "rebound after its definition" in e["m"] or "runtime value is not the one the model reads" in e["m"] or "`global` declaration" in e["m"]),
    ("ISBOOL `x is True/False` identity", lambda e: "IDENTITY test against a `bool`" in e["m"]),
    ("HETERO heterogeneous list literal", lambda e: "heterogeneous" in e["m"]),
    ("ARRAY-REASSIGN array local from non-literal RHS", lambda e: "reassigning an array LOCAL" in e["m"]),
    ("OBJSTATE class instantiation (_pyobj_state)", lambda e: "_pyobj_state" in e["m"] or "__new__" in e["m"] or "non-trivial `__n" in e["m"]),
    ("EFFECT write effect inside a pure expression (call with effects in comprehension/cond/arg)", lambda e: "write effect does not happen" in e["m"]),
    ("SYNTAX emitter produced ill-formed WhyML", lambda e: e["m"].startswith("syntax error")),
    ("FLOAT real-valued field", lambda e: "type real" in e["m"]),
    ("CALLABLE first-class function value applied", lambda e: "cannot be applied" in e["m"]),
    ("TUPLE tuple return slot / tuple unpack typing", lambda e: "This pattern has type (" in e["m"] or "pytuple" in e["m"] or re.search(r"type \((\w|')+, ", e["m"]) is not None or e["a"] == "unpack->phs"),
    ("EXT stdlib/external call erased to 0-ary input-blind val (pathlib/os/json/hashlib/io)", lambda e: re.search(r"\b(path_\w+_\d+ \(\)|\w+_read_text_\d+ \(\)|\w+_read_bytes|f_read_\d+|_cwd_\d+|hashlib|loads \(|\w+_hexdigest|encode_\d+ \(\)|os_path|_os_|json_|\w+_iterdir|\w+_glob|\w+_exists_\d+|\w+_resolve_\d+|time_\w+|re_\w+_\d+|_match_\d+|\w+_group_\d+)", e["n"] + " " + e["el"]) is not None or re.search(r"\b(Path\(|\.read_text\(|\.read_bytes\(|\.read\(\)|hashlib\.|json\.(loads|dumps|load)|os\.path\.|os\.walk|os\.listdir|\.iterdir\(|\.glob\(|\.exists\(\)|re\.(match|search|sub|compile|findall|fullmatch|finditer|split)|\.group\(|time\.|shlex\.|tempfile\.|inspect\.|sys\.)", e["s"] + " " + e["r"]) is not None and re.search(r"type int, but|but is expected to have type int\b|\(\)\)", e["m"] + e["n"]) is not None),
    ("GETATTR AST getattr / hasattr / getter erasure", lambda e: re.search(r"pycsl_getattr|getattr_unknown|\(get_\w+ |\bget_\w+ !", e["n"] + " " + e["el"]) is not None or re.search(r"\b(getattr|hasattr|setattr)\(", e["s"]) is not None),
    ("FSTR f-string / str literal hashed into int str_concat", lambda e: re.search(r"str_concat|\b\d{7,}\b", e["n"]) is not None and ("string" in e["m"] or "int" in e["m"]) and (re.search(r"f['\"]|['\"] *\+|\+ *['\"]|%", e["s"] + e["r"]) is not None or "str_concat" in e["n"])),
    ("STRM str method erasure (split/strip/startswith/join/...)", lambda e: re.search(r"\.(%s)\(" % STRM, e["r"] or "") is not None or re.search(r"_(%s)_\d+" % STRM, e["n"] + " " + e["el"]) is not None or (re.search(r"\.(%s)\(" % STRM, e["s"]) is not None and re.search(r"string|array", e["m"]) is not None)),
    ("STRPLUS string `+`/`*`/`%` lowered as int arithmetic", lambda e: re.search(r"['\"]\s*\+|\+\s*['\"]|\+=\s*['\"]", e["s"] + " " + e["r"]) is not None and "string" in e["m"]),
    ("MEMB `in`-membership on a container erased to int ('mu -> 'mu1)", lambda e: "'mu -> 'mu1" in e["m"]),
    ("SET set()/frozenset value typed (StrSet / Array.make 1024 / membership)", lambda e: "StrSet" in e["m"] or "Array.make 1024 0" in e["n"] or re.search(r"\bset\(|frozenset\(|: Set\[|: set\b", e["s"] + " " + e["r"]) is not None),
    ("DICT Dict[str,Any] IR-dict: heterogeneous values typed `string -> option int` (Map.get value read as str/dict/list)", lambda e: re.search(r"-> option\.Option\.option|-> option\. Option", e["m"]) is not None or re.search(r"Map\.get|subscript_get|\w+_get_\d+ ", e["n"] + " " + e["el"]) is not None or re.search(r"\.get\(|\.items\(\)|\.keys\(\)|\.values\(\)|: dict\b|: Dict\[|= \{", e["s"] + " " + e["r"]) is not None),
    ("GENEXP generator / comprehension / any()/all()/sorted() erasure", lambda e: re.search(r"\(any (int|\(array int\)|bool)\)|any_\d+ ", e["n"] + " " + e["el"]) is not None or re.search(r"\bfor \w+(, \w+)* in\b.*[\]\)]|\b(any|all|sorted|sum|min|max|enumerate|zip|reversed|map|filter)\(", e["s"] + " " + e["r"]) is not None),
    ("LISTSTR List[str]/List[T] local or field typed array int (element typing)", lambda e: re.search(r"array\.Array\.array int @rho\d*, but is expected to have type array\.Array\.array (string|PyCSL)|seq\.Seq\.seq int, but is expected to have type seq\. ?Seq\.seq (string|PyCSL)|array\.Array\.array string @rho\d*, but is expected to have type array\.Array\.array int|seq\.Seq\.seq string, but is expected to have type int|seq\.Seq\.seq", e["m"]) is not None or re.search(r": (List|list)\[", e["s"]) is not None or re.search(r"array", e["m"]) is not None),
    ("PYVAL IR-dict node (pyval) vs erased int local", lambda e: "pyval" in e["m"]),
    ("OPTREC Optional[record] / None where a record (or tuple) is expected", lambda e: e["n"].strip() in ("pycsl_none", "py_none") or ("return None" in e["s"] and "PyCSL_Program" in e["m"])),
    ("RECORD record/ADT value (emit_ir/term/classdef/stmt) vs erased int local", lambda e: re.search(r"PyCSL_Program\. ?\w+", e["m"]) is not None),
    ("UNIT unit-returning call used as a value", lambda e: "type ()" in e["m"]),
    ("REF ref vs value (mutable-local aliasing)", lambda e: "ref 'mu" in e["m"] or "type ref " in e["m"]),
    ("UNBOUND unbound symbol (missing helper/val/field)", lambda e: "unbound" in e["m"]),
    ("INTSTR int<->string erasure (upstream local/param typed int)", lambda e: re.search(r"type (int|string), but is expected to have type (string|int)\b", e["m"]) is not None),
    ("BOOL bool vs int", lambda e: re.search(r"type bool, but|expected to have type bool", e["m"]) is not None),
]


def ev(c):
    m = re.sub(r"/home/\S+", "", c.get("msg", "")); m = " ".join(m.split())
    m = m.split(" UserWarning")[0]
    return {"m": m, "s": c.get("stmt") or "", "n": c.get("snip") or "", "r": c.get("root_rhs") or "", "a": c.get("act") or "",
            "el": c.get("errline") or ""}


PHRE = re.compile(r"^\w+(: [^=]+)? = (0|\"\"|''|\[\]|False|None|\[0\]|\[''\]|\[\"\"\])$|^HDR (If|While) False$|^HDR For .* in \[\]$")


def fam(c):
    e = ev(c)
    if PHRE.match(e["s"].strip()) or e["a"] == "PH-CONFLICT": return "PH"
    for name, p in RULES:
        try:
            if p(e): return name.split(" ")[0].replace("MUTRECV2", "MUTRECV")
        except Exception:
            pass
    return "OTHER"


FAMNAME = {name.split(" ")[0]: name for name, _ in RULES}
FAMNAME["OTHER"] = "OTHER unclassified"
FAMNAME["RIPPLE"] = "RIPPLE ported body type-checks; the error moved to a mirror CALLER / class type decl (live signature/field types differ from the mirror's)"
FAMNAME["PH"] = "PH placeholder-induced conflict (census artifact; chain tail unknown)"
FAMNAME["LOCATE"] = "LOCATE blocker outside the ported body (caller ripple / helper) - tail unknown"

if __name__ == "__main__":
    C = collections.Counter(); ex = collections.defaultdict(list)
    for l in open(sys.argv[1]):
        j = json.loads(l)
        for c in j.get("chain", []):
            f = fam(c); C[f] += 1
            if len(ex[f]) < int(sys.argv[2] if len(sys.argv) > 2 else 4):
                e = ev(c); ex[f].append(f"{j['qual'][-35:]} | {e['s'][:80]} | {e['m'][:90]} | {e['n'][:50]}")
    for f, n in C.most_common():
        print(n, FAMNAME.get(f, f))
        for x in ex[f]: print("     ", x)
