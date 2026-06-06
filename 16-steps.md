
Here are 16 steps, that I want you to follow, from 0 to 15. Save this plan in `./min-std-lib.md`. Write it in the right format so that it can be executed with `./bin/agent-feature-supervisor --feature-file min-std-lib.md`.

# Reference Example

I showed an example of how I want each standard library to be stubbed and tested. The example I wrote is now in `unix-filesystem/`:
- core underlying concepts of unix file systems are in a global variable with type UnixInodeFileSystem.py
- the replacement for the standard library `os` is in `my_os.py` (should be merged into `src/pycsl_lib/os.py` the place for standard library stubs).
- the formal test driver `my_os_demo.py` enabling a full end-to-end formal validation of the feature. Similar formal test drivers should be used.

I just added a skill named `config/skills/unix` so that you get a better understanding of some underlying concepts used by the standard library, to create other class playing a role similar to `unix-filesystem/UnixInodeFileSystem.py`.

When in doubt refer to:
- `unix-filesystem/` an example to stub some system calls,
- `config/skills/unix` generic unix knowledge,
- `test-suite/library_reference/` the behavior of official Python Standard Libraries.

---

# The 16 steps

Items range from 0 to 15. Item 1 to 15 should follow something similar to what was done in `unix-filesystem/`:
- classes with contract to bear what is done (like `class UnixInodeFileSystem`), either for global variables or returned types by standard library,
- Annotated Python classes without `\trusted` which are stubbing Python's standard library,
- Formal test drivers to exercice contracts of standard library stubs (similar to previous `unix-filesystem/my_os_demo.py`).

## 0. Initial tasks
The your single highest-leverage target isn't a module at all — it's the builtins your own doc flags (isinstance, set ops, dict membership, and open). It is the prerequisite under everything below. Implement `os` in `src/pycsl_lib/` using the model given in `unix-filesystem/` with `my_os.py` being integrated in `src/pycsl_lib/os.py` and `UnixInodeFileSystem.py` being copied under `src/pycsl_lib/os/`

## 1. os.path
The obvious sibling to your os work, but cheaper: join, dirname, basename, splitext, normpath are pure string functions with no filesystem state. You get a clean path algebra for almost free, it's in nearly every file-handling program (including your CLI), and it complements the inode model without dragging in more global state. Do this first; it's the fastest ROI on the list.

## 2. io + builtin open
Here's the under-appreciated point: real Python file code rarely calls os.open/read; it calls open() and gets an io object. So for application verification, the io stream layer (position, buffer contents, open/closed state) matters more than raw fds — and it's exactly what Module1_Ingestor does when it reads source. Stateful like the FS, pairs directly with your os model, and is on the self-annotation path.

## 3. ast
Your Bucket B blocker, and strategically the most important thing here even though its general popularity is low. You cannot body-verify Module2_Parser/Module3_Weaver without modeling the AST node zoo and NodeVisitor dispatch. The good news: the node set is large but structurally regular — it's an algebraic data type, which is the friendliest possible shape for a WhyML model. This is the gate to the "big change" we discussed.

## 4. collections deque, Counter, defaultdict, namedtuple
Modeling these buys you reusable abstractions: Counter is a multiset (maps to a bag theory), defaultdict is a total map, deque is a sequence. The payoff isn't the module itself; it's that every downstream proof over client code that uses them inherits clean algebraic reasoning. High reuse, high tractability.

## 5. re
Enormous ubiquity, and the one module where a partial model already pays for itself: match/search return Optional[Match], groups have known arity, and you sidestep the exception cases. The bonus is security — ReDoS/catastrophic backtracking is a real, sound-analysis-detectable defect (Mopsa published on exactly this). Don't try to model full regex semantics; model the API surface and the no-raise contract first.

## 6. json
Your IR is JSON; your agent pipeline round-trips it constantly. The interesting modeling object is the recursive union type (dict | list | str | int | float | bool | None), and the valuable contract is the round-trip property (loads(dumps(x)) == x under stated constraints). Directly self-annotation-relevant via Module5_IREmitter and the agent I/O.

## 7. typing
You mandate type annotations, so modeling Optional/Union/List[T]/Dict[K,V] lets you turn the type layer into free contract facts — types as cheap invariants feeding Why3, the lightweight cousin of the abstract-interpretation idea from earlier. Strategic for self-annotation and a force-multiplier on every other module here.

## 8. math
Split it. The integer functions (gcd, isqrt, factorial, comb, perm) are pure, clean, map onto Why3's int theory, and are exactly the territory of your own GCD showcase — do these. The float transcendentals (sin, log, sqrt) need real/float axiomatization and are where it gets expensive; defer or lean on Why3's real theory carefully. Model the cheap, high-yield half now.

## 9. sys
argv (list of str), exit (maps to your \diverges), maxsize, recursionlimit. Mostly trivial values plus one effect you already have machinery for. Cheap, and every CLI uses it — including pycsl.py itself.

## 10. bisect
Tiny, pure, and it plugs straight into contract predicates you already have (\is_sorted, \sum). Binary search and sorted insertion are high-yield for array reasoning and cost almost nothing to specify. Quick win that immediately strengthens algorithm proofs.

## 11. functools
reduce is a fold (clean inductive spec). lru_cache is the interesting one: memoization is sound iff the function is referentially transparent — modeling it makes you formalize purity, which connects to your assigns \nothing reasoning and is a genuinely elegant contract. partial drags in closures (which you've flagged as hard), so scope around it.

## 12. enum
Finite domains mapping to clean algebraic/finite types — and crucially, token kinds in parsers are usually enums, so your own Lark-based code likely needs this. Cheap to model, common, and it sharpens dispatch-exhaustiveness proofs (the "all 10 WP arms" property generalizes to "all enum cases").

## 13. dataclasses
The idiomatic way to write record classes, and you already showed a class-as-mutable-record WhyML encoding. Modeling the auto-generated __init__/__eq__ is the natural extension, and if your IR/AST node classes are dataclasses (they often are), this is on the self-annotation path too.

## 14. itertools
High ubiquity, but model only the eager/bounded operators (chain, islice, product, combinations) with finite specs first. The lazy/infinite generator semantics are genuinely hard (coroutine state, non-termination) and collide with the generator-modeling problem — explicitly defer that half rather than letting it block the easy wins.

## 15. heapq
Rounds out your algorithm-verification capability alongside bisect: a clean heap-invariant spec (heappush/heappop preserve the min-heap property) over an ordinary list. Self-contained, reusable, and a satisfying functional-correctness target.

---

# Conclusion

Save this plan in `./min-std-lib.md`. Write it in the right format so that it can be executed with `./bin/agent-feature-supervisor --feature-file min-std-lib.md`.