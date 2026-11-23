"""CR.py <out> <witness.py>... : the REAL _census_row of bin/check-refusal-witness-coverage.py on each witness
(cwd = tree root, witness path relative, the committed census's form); prints the rows to <out>."""
import sys, os, importlib.util
out, *ws = sys.argv[1:]
spec = importlib.util.spec_from_file_location("rwc", "bin/check-refusal-witness-coverage.py")
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
with open(out, "w") as fh:
    for w in ws:
        fh.write(m._census_row(os.path.join(os.getcwd(), ".venv", "bin", "python3"), w))
