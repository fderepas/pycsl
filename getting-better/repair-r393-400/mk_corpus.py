#!/usr/bin/env python3
"""mk_corpus.py <mk.tsv> <probe-dir> : write the corpus witnesses / controls of the r393-r400 repair."""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
W = os.path.join(ROOT, "getting-better", "open-routes")
for line in open(sys.argv[1]):
    if not line.strip():
        continue
    nid, exp, name, src, desc = line.rstrip("\n").split("\t")
    kind, path = src.split(":", 1)
    body = open(os.path.join(W if kind == "W" else sys.argv[2], path)).read()
    tag = "expected FAIL" if exp == "FAIL" else "expected PASS"
    hdr = 'r"""Test %s -- gen #37 %s (%s): %s\n"""\n# pycsl-expected: %s\n' % (nid, desc.split(":")[0], tag, desc.split(":", 1)[1].strip(), exp)
    out = os.path.join(ROOT, "test-suite", "corpus", "pycsl-reference", "%s_%s.py" % (nid, name))
    open(out, "w").write(hdr + body)
    print(out)
