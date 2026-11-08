import sys, hashlib, itertools, struct as pystruct
sys.path.insert(0, "src/pycsl")
from module6_whyml.struct_format import parse_format
M = 2147483647
def sh(s): return int(hashlib.sha256(s.encode("utf-8")).hexdigest()[:8], 16) % M
def key(raw):
    try:
        p = parse_format(raw)
    except Exception:
        return None
    if p is None: return None
    try:
        sid = p.slot_id()
        ft = getattr(p, "faithful_tag", None)
        ft = ft() if callable(ft) else ft
        bn = getattr(p, "bytes_n", None)
        bn = bn() if callable(bn) else bn
    except Exception:
        return None
    return (sid, ft, bn, p.arity)
prefixes = ["<", ">", "=", "!"]
codes = "bBhHiIlLqQ"
seen = {}
n = 0
found = []
# formats: prefix + interleaved pads and two int codes
pads = [""] + ["x"*k for k in range(1,9)] + [f"{k}x" for k in range(2,9)]
for pre in prefixes:
    for c1 in codes:
        for c2 in codes:
            for p1 in pads:
                for p2 in pads:
                    for p3 in pads:
                        raw = pre + p1 + c1 + p2 + c2 + p3
                        k = key(raw)
                        if k is None: continue
                        n += 1
                        h = sh('"' + raw + '"')
                        kk = (k, h)
                        if kk in seen and seen[kk] != raw:
                            other = seen[kk]
                            # CPython-observable difference?
                            try:
                                a = pystruct.pack(raw, 1, 2)
                                b = pystruct.pack(other, 1, 2)
                            except Exception:
                                continue
                            if a != b:
                                found.append((other, raw, h, k, b, a))
                                print("PAIR", repr(other), repr(raw), "hash", h, "key", k); print("   CPython pack(..,1,2):", b.hex(), "vs", a.hex()); sys.stdout.flush()
                                if len(found) >= 3:
                                    raise SystemExit(0)
                        seen[kk] = raw
print("candidates scanned:", n, "collisions:", len(found))
for o, r, h, k, b, a in found:
    print("PAIR", repr(o), repr(r), "hash", h, "key", k)
    print("   CPython pack(...,1,2):", b.hex(), "vs", a.hex())
