"""Mechanical clause-survival census: for each corpus file, compare the number of source
`#@ requires` / `#@ ensures` clauses against the number of `requires {` / `ensures {`
lines in the emitted .mlw. The emitter ADDS clauses (frame preservation, exception
triggers, class invariants), so emitted < source is a candidate DROPPED CLAUSE."""
import os, re, io, tokenize
CORP = 'test-suite/corpus/pycsl-reference'
EMIT = 'scratchpad/w8/emit_r14b'
bad = []
n = 0
for f in sorted(os.listdir(CORP)):
    if not f.endswith('.py'):
        continue
    mlw = os.path.join(EMIT, f[:-3] + '.mlw')
    if not os.path.exists(mlw):
        continue
    src = open(os.path.join(CORP, f), encoding='utf-8').read()
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except Exception:
        continue
    s_req = s_ens = 0
    for t in toks:
        if t.type != tokenize.COMMENT:
            continue
        st = t.string.strip()
        if st.startswith("#@ requires"):
            s_req += 1
        elif st.startswith("#@ ensures"):
            s_ens += 1
    text = open(mlw, encoding='utf-8').read()
    e_req = len(re.findall(r"^\s*requires\s*\{", text, re.M))
    e_ens = len(re.findall(r"^\s*ensures\s*\{", text, re.M))
    n += 1
    if e_req < s_req or e_ens < s_ens:
        bad.append((f, s_req, e_req, s_ens, e_ens))
print("corpus files compared:", n)
print("files where an emitted clause count is BELOW the source count:", len(bad))
for b in bad[:40]:
    print("   %-46s requires %d->%d  ensures %d->%d" % b)
