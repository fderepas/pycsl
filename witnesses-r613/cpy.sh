#!/bin/bash
# route #613: which file does CPython ACTUALLY load? (rule 30). Benign probes only; each run is
# ulimit'd (rule 3). Script-directory shapes (j0 j1 h0 h1 n1) and the corpus witnesses' layout
# (PYTHONPATH = the --import-path root, the root order pycsl assumes).
W=/home/fabrice/git/pycsl-u52/witnesses-r613
C=/home/fabrice/git/pycsl-u52/test-suite/corpus/pycsl-reference
for py in /usr/bin/python3 /home/fabrice/git/pycsl-u52/.venv/bin/python3; do
  echo "#### interpreter $py ($($py -c 'import sys; print(sys.version.split()[0])'))"
  for d in j0 j1 h0 h1 n1 s1; do
    echo "== $d (script dir)"; (cd /tmp && timeout 60 bash -c "ulimit -v 2000000; $py -B $W/$d/prog.py" 2>&1)
    # the same directory as sys.path[0] ('' under -c with cwd = the program's directory)
    (cd $W/$d && timeout 60 bash -c "ulimit -v 2000000; $py -B -c 'import sys, json, hashlib; print(\"  -c in dir:\", {k: getattr(sys.modules.get(k), \"__file__\", None) for k in (\"re\", \"_hashlib\", \"sitecustomize\")})'" 2>&1)
  done
  for f in $C/1018[0-8]_r613_*.py; do
    root=$(grep -m1 '^# pycsl-flags:' $f | sed 's/.*--import-path //')
    probe='import sys; import json, hashlib, platform; print({k: getattr(sys.modules.get(k), "__file__", None) for k in ("re", "_hashlib", "codecs", "r613_helper", "sitecustomize")})'
    echo "== $(basename $f) PYTHONPATH=${root:-<none>}"
    (cd /tmp && PYTHONPATH=${root:+/home/fabrice/git/pycsl-u52/$root} timeout 60 bash -c "ulimit -v 2000000; $py -B $f; $py -B -c '$probe'" 2>&1 | tail -3)
  done
done
