#!/bin/bash
# Mutation test: perturb source, re-emit .mlw, confirm the emitted text MOVES, restore.
set -e
SRC=src/self-annotate/src/module6_whyml/ir_scanner.py
MLW=src/self-annotate/src/module6_whyml/ir_scanner.mlw
emit() { find src/pycsl -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null; rm -f "$MLW"; PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py "$SRC" --import-path src/pycsl --no-proof --no-typecheck --keep-mlw >/dev/null 2>&1; }
cp "$SRC" /tmp/cm_src.bak

echo "=== baseline emit ==="
emit
echo "member 'setdefault' present: $(grep -c 'pystr_eq mm \"setdefault\"' $MLW)"
echo "sep '.' hassep present: $(grep -c '__hassep f \".\"' $MLW)"
echo "tag 'ArraySet' present: $(grep -c 'pystr_eq tag \"ArraySet\"' $MLW)"

echo "=== MUT1: member setdefault -> setZZ ==="
sed -i "s/'setdefault'/'setZZ'/" "$SRC"; emit
echo "  setZZ now present: $(grep -c 'pystr_eq mm \"setZZ\"' $MLW) (expect 1); setdefault gone: $(grep -c 'pystr_eq mm \"setdefault\"' $MLW) (expect 0)"
cp /tmp/cm_src.bak "$SRC"

echo "=== MUT2: rsplit sep '.' -> ':' (both the 'in' test and rsplit) ==="
sed -i 's/if "\." in func/if ":" in func/; s/func.rsplit("\.", 1)/func.rsplit(":", 1)/' "$SRC"; emit
echo "  hassep f \":\" present: $(grep -c '__hassep f \":\"' $MLW) (expect 1); hassep f \".\" gone: $(grep -c '__hassep f \".\"' $MLW) (expect 0)"
cp /tmp/cm_src.bak "$SRC"

echo "=== MUT3: tag 'ArraySet' -> 'ArraySetZ' ==="
sed -i 's/== "ArraySet"/== "ArraySetZ"/' "$SRC"; emit
echo "  ArraySetZ present: $(grep -c 'pystr_eq tag \"ArraySetZ\"' $MLW) (expect 1); ArraySet-exact gone: $(grep -c 'pystr_eq tag \"ArraySet\"' $MLW) (expect 0)"
cp /tmp/cm_src.bak "$SRC"

echo "=== restore + re-emit baseline ==="
emit
echo "restored; setdefault present again: $(grep -c 'pystr_eq mm \"setdefault\"' $MLW)"
rm -f /tmp/cm_src.bak
