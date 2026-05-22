SHELL := /bin/bash

PROJECT_ROOT := /home/fabrice.derepas@canonical.com/git/pycsl
PYTHON := /home/fabrice.derepas@canonical.com/git/pycsl/.venv/bin/python
PYCSL := $(PROJECT_ROOT)/src/pycsl/pycsl.py
ROCQ_AGENT := $(PROJECT_ROOT)/src/pycsl/agents/agent-rocq-proof-writer.py
INPUT := /home/fabrice.derepas@canonical.com/git/pycsl/test-suite/corpus/pycsl-reference/0288.py
PROOF_DIR := $(CURDIR)

.PHONY: help replay coq llm clean

help:
	@echo "Targets:"
	@echo "  make replay  - replay proofs with pycsl --rocq-proofs"
	@echo "  make coq     - compile all .v files with coqc"
	@echo "  make llm     - rerun agent-rocq-proof-writer.py on all .v files"
	@echo "  make clean   - remove Rocq compilation artifacts and *.llm.log"

replay:
	cd "$(PROJECT_ROOT)" && "$(PYTHON)" "$(PYCSL)" --rocq-proofs "$(PROOF_DIR)" "$(INPUT)"

coq:
	"$(PROJECT_ROOT)/bin/run-rocq-proofs.sh" "$(PROOF_DIR)"

llm:
	@set -euo pipefail; 	shopt -s nullglob; 	mlw=""; 	for f in "$(CURDIR)"/*.mlw; do mlw="$$f"; break; done; 	count=0; 	for v in "$(CURDIR)"/*.v; do 		count=$$((count + 1)); 		echo "[*] LLM proof $$v"; 		if [[ -n "$$mlw" ]]; then 			cd "$(PROJECT_ROOT)" && "$(PYTHON)" "$(ROCQ_AGENT)" --in "$$v" --out "$$v" --mlw "$$mlw"; 		else 			cd "$(PROJECT_ROOT)" && "$(PYTHON)" "$(ROCQ_AGENT)" --in "$$v" --out "$$v"; 		fi; 	done; 	if [[ $$count -eq 0 ]]; then 		echo "[!] No .v files found in $(CURDIR)"; 		exit 1; 	fi

clean:
	rm -f *.glob *.vo *.vok *.vos *.llm.log *~
