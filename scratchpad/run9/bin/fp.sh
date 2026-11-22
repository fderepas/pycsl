#!/bin/bash
# fp.sh <tree> : proof-tooling fingerprint (run #9 proof-map rule).
#  vac = sha of pycsl.py from `_BODY_EQ_RE` up to `def main` (vacuity gate, probe builders, why3 / prover dispatch, _run_proofs)
#  py  = whole pycsl.py blob (informational: front-end changes show up in the EMISSION check)
#  bin = bin/ tree hash; conf = ~/.why3.conf; pv = why3 / alt-ergo / z3 versions
T=$1; c=$(git -C $T rev-parse HEAD)
vac=$(git -C $T show $c:src/pycsl/pycsl.py | sed -n '/^_BODY_EQ_RE/,/^def main/p' | sha256sum | cut -c1-10)
pv=$( (why3 --version; alt-ergo --version; z3 --version) 2>/dev/null | tr -d '\n' | sha256sum | cut -c1-8)
d=$(git -C $T status --porcelain -- src/pycsl bin | wc -l)
echo "vac=$vac py=$(git -C $T rev-parse $c:src/pycsl/pycsl.py | cut -c1-10) bin=$(git -C $T rev-parse $c:bin | cut -c1-10) conf=$(sha256sum ~/.why3.conf 2>/dev/null | cut -c1-10) pv=$pv dirty=$d"
