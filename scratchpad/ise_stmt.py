    def _is_string_expr(self, ir: "ExprIR") -> bool:
        return True

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
    #@ assigns \nothing
    def _track_collection_metadata(self, target: str, val_ir: "ExprIR") -> None:
        return

    #@ \trusted reviewer: pycsl-self-annotate
    #@ ensures True
