Let's consirder the following loop of agents:
```
    └── agent-splitter.py — call-graph analysis, topological sort
        └── agent-writer.py — per-function annotation (3-agent pipeline)
            ├── agent-english-writer.py  — English spec of the function
            ├── agent-contract-writer.py — requires/ensures/assigns
            └── agent-invariant-writer.py — loop invariants & variants
```
Write a bash script `./bin/call-agent-splitter.sh` which launch the loop above on a given example. Here is an example of usage:
```
./bin/call-agent-splitter.sh foobar/Module6_WhyMLTranspiler.py --class IRScanner --fun _handle_assign_stmt
```
Here is the expected result for `agent-english-writer.py`:
  ``` _handle_assign_stmt in Module6_WhyMLTranspiler.py is the code generator for Python assignment statements — it translates one IR assignment node into a WhyML string.                                     
            Formal correspondent: wp SAssign arm in Phase4_WP.v:23–24:                                                                                                                                      
      wp (SAssign x e) Q  :=  [x ↦ eval_expr σ e] Q                                                                       
      The WP rule says: the precondition needed to guarantee Q after assigning e to x is just Q with every free occurrence of x replaced by the value of e. In WhyML this becomes a let binding or a reference 
      update (x := expr).                                                                                                
      What the method does concretely:                                                                                    
      1. Translates the RHS expression — calls _expr_to_whyml on the IR expression node to produce the WhyML expression string (this may register abstract operation declarations as a side effect, which is   
  why                                                                                                                       
      assigns self._abstract_ops).                                                                                        
      2. Determines the binding form — decides whether the assignment becomes a let x = ... (immutable, first use) or x := ... (mutable reference update, subsequent use), depending on whether x is already   
  in                                        
      declared_refs.                                                                                                                                                                                           
      3. Updates collection-tracking state — if the assignment target is a collection (array, dict, lambda, record), it records that fact in the relevant instance variable (_array_locals, _dict_locals,      
  etc.)                                                                                                                                                                                                        
      so that downstream handlers can generate correct typed WhyML for subsequent accesses to that variable. This is why the assigns clause is so wide.                                                        
      4. Returns the WhyML string — a non-empty string like "let x = expr in\n" or "x := expr;\n".                                                                                                             
                                                                                                                                                                                                               
      Why the assigns clause is wide: Unlike the formal model (where state is a pure association list and the assignment is a single substitution), the Python implementation also propagates type information 
      forward through mutable instance variables. The assigns clause makes this explicit — _handle_assign_stmt is not pure; it has tracked side effects that affect how all subsequent statements in the same  

  ```
Here is the expected result for the final annotation:
```
      # Formal correspondent: wp SAssign (Phase4_WP.v:23-24)
      # wp (SAssign x e) Q := [x ↦ eval_expr σ e] Q
      # Side effect: also mutates declared_refs (adds target); not expressible in assigns syntax.
      #@ requires stmt != 0
      #@ requires \length(rest) >= 0
      #@ ensures \result != ""
      #@ assigns self._known_collection_sizes, self._known_collection_elements
      #@ assigns self._array_locals, self._dict_locals, self._lambda_locals
      #@ assigns self._record_locals, self._abstract_ops
      def _handle_assign_stmt(self, stmt: Dict[str, Any], rest: List[Dict[str, Any]],
```
Provide recommendations and draft a new plan in `./plan-annotate-??.md` where ?? is a new number compared to existing ones.
Example of recommendation:
- `agent-splitter.py` should write a text detalling the global intent in order to have a better quality of the code.
- `agent-english-writer.py` should have an understand of Python code in order to give more precise recommendation and should also get the brief from agent-splitter.
- `agent-english-writer.py` should have an understand of Python code being called.
