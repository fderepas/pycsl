#!/usr/bin/env python3
"""Smoke test: parse every `#@` contract in the corpus + stdlib with the
hand-written recursive-descent parser and report any parse failures.

Originally the Step-4 differential gate of `no-lark-plan.md` (it compared
the Lark engine's tree against the rdp engine's tree, requiring 0 mismatches
before the Lark layer was deleted). With Lark now removed, this remains a
standing corpus-parse regression test: every `#@` contract in
`test-suite/corpus/pycsl-reference/` and `src/pycsl_lib/` must still parse.
"""
import sys, glob, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "pycsl"))

from frontend.Module1_Ingestor import Module1_Ingestor
from frontend.Module2_Parser import Module2_Parser

CORPUS = sorted(glob.glob("test-suite/corpus/pycsl-reference/*.py"))
STDLIB = sorted(glob.glob("src/pycsl_lib/**/*.py", recursive=True))


def collect_contracts(files):
    for f in files:
        src = open(f).read()
        try:
            contracts = Module1_Ingestor(src).process()
        except Exception as e:
            print(f"WARN: Module1 failed on {f}: {e}")
            continue
        for c in contracts:
            for s in c.contracts:
                yield f, c.line_number, s


def main():
    p = Module2_Parser()
    total = errors = 0
    samples = []
    for f, ln, s in collect_contracts(CORPUS + STDLIB):
        total += 1
        try:
            p.parse_contract(s, ln)
        except Exception as e:
            errors += 1
            if len(samples) < 20:
                samples.append((f, ln, s, f"{type(e).__name__}: {e}"))
    print(f"Total contracts: {total}")
    print(f"  parsed OK:     {total - errors}")
    print(f"  errors:        {errors}")
    for f, ln, s, msg in samples:
        print("=" * 70)
        print(f"{f}:{ln}  {s!r}")
        print(f"  {msg[:300]}")
    return 0 if errors == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
