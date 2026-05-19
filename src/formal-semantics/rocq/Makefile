COQC     := coqc
COQFLAGS := -R . PyCSL
VFILES   := Phase1_AST.v Phase2_State.v Phase3_SOS.v Phase3b_Desugar.v \
            Phase4_WP.v Phase5a_WhileInv.v Phase5b_Soundness.v Tests.v
VOFILES  := $(VFILES:.v=.vo)

all: $(VOFILES)

proof: all
	@echo "=== PyCSL Rocq proof status ==="
	@echo "Files compiled: $(words $(VFILES))"
	@admitted=$$(grep -cl 'Admitted' $(VFILES) 2>/dev/null | wc -l); \
	 echo "Files with Admitted: $$admitted"; \
	 if [ "$$admitted" -gt 0 ]; then \
	   grep -n 'Admitted' $(VFILES) | sed 's/^/  /'; \
	 fi
	@echo "=== All proofs checked ==="

# Dependency chain
Phase1_AST.vo: Phase1_AST.v
Phase2_State.vo: Phase2_State.v Phase1_AST.vo
Phase3_SOS.vo: Phase3_SOS.v Phase1_AST.vo Phase2_State.vo
Phase3b_Desugar.vo: Phase3b_Desugar.v Phase1_AST.vo Phase2_State.vo Phase3_SOS.vo
Phase4_WP.vo: Phase4_WP.v Phase1_AST.vo Phase2_State.vo Phase3_SOS.vo Phase3b_Desugar.vo
Phase5a_WhileInv.vo: Phase5a_WhileInv.v Phase1_AST.vo Phase2_State.vo Phase3_SOS.vo Phase3b_Desugar.vo Phase4_WP.vo
Phase5b_Soundness.vo: Phase5b_Soundness.v Phase1_AST.vo Phase2_State.vo Phase3_SOS.vo Phase3b_Desugar.vo Phase4_WP.vo Phase5a_WhileInv.vo
Tests.vo: Tests.v Phase1_AST.vo Phase2_State.vo Phase3_SOS.vo Phase3b_Desugar.vo Phase4_WP.vo Phase5a_WhileInv.vo Phase5b_Soundness.vo

%.vo: %.v
	$(COQC) $(COQFLAGS) $<

clean:
	rm -f *.vo *.glob *.vok *.vos .*.aux

.PHONY: all proof clean
