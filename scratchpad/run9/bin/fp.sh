#!/bin/bash
# fp.sh <tree> : proof-tooling fingerprint = pycsl.py blob + bin/ tree + src/pycsl tree-level prover config + why3/prover versions + why3.conf hash
T=$1; c=$(git -C $T rev-parse HEAD)
d=$(git -C $T status --porcelain -- src/pycsl bin | wc -l)
echo "py=$(git -C $T rev-parse $c:src/pycsl/pycsl.py | cut -c1-10) bin=$(git -C $T rev-parse $c:bin | cut -c1-10) conf=$(sha256sum ~/.why3.conf 2>/dev/null | cut -c1-10) dirty=$d"
