# ACSL & MetAcsl — Patterns and Worked Examples

Copy-adaptable templates. Each shows the *idiom*, not just a syntax fragment.
Adapt names, bounds, and types; keep the structure.

## 1. Bounded array read with functional postcondition

```c
/*@ requires \valid_read(a + (0 .. n-1));
    requires n > 0;
    assigns  \nothing;
    ensures  \forall integer i; 0 <= i < n ==> a[i] <= \result;
    ensures  \exists integer i; 0 <= i < n && a[i] == \result;
*/
int array_max(const int* a, int n);
```
The two postconditions together pin down "the maximum": an upper bound *and*
attainment. One alone is too weak.

## 2. Loop: the invariant/assigns/variant triad

```c
/*@ requires \valid(a + (0 .. n-1));
    assigns  a[0 .. n-1];
    ensures  \forall integer k; 0 <= k < n ==> a[k] == 0;
*/
void zero(int* a, int n) {
  /*@ loop invariant 0 <= i <= n;
      loop invariant \forall integer k; 0 <= k < i ==> a[k] == 0;
      loop assigns i, a[0 .. n-1];
      loop variant n - i;
  */
  for (int i = 0; i < n; i++) a[i] = 0;
}
```
Note the invariant carries **both** the index bound (`0 <= i <= n`) and the
"work done so far" (`a[k]==0` for `k<i`). The first is what makes the second
inductive.

## 3. Search loop with a found/not-found postcondition

```c
/*@ requires \valid_read(a + (0 .. n-1));
    assigns  \nothing;
    behavior found:
      assumes  \exists integer k; 0 <= k < n && a[k] == v;
      ensures  0 <= \result < n && a[\result] == v;
    behavior not_found:
      assumes  \forall integer k; 0 <= k < n ==> a[k] != v;
      ensures  \result == -1;
    complete behaviors;
    disjoint behaviors;
*/
int find(const int* a, int n, int v);
```

## 4. Predicate + axiomatic for a recursive notion

```c
/*@ predicate sorted(int* a, integer n) =
      \forall integer i, j; 0 <= i <= j < n ==> a[i] <= a[j];

    axiomatic Sum {
      logic integer sum(int* a, integer lo, integer hi) reads a[lo .. hi-1];
      axiom sum_empty: \forall int* a, integer lo; sum(a, lo, lo) == 0;
      axiom sum_rec:   \forall int* a, integer lo, hi; lo < hi ==>
                         sum(a, lo, hi) == sum(a, lo, hi-1) + a[hi-1];
    }
*/
```
Use `predicate`/`logic` for direct equations; use `axiomatic` only when the
definition is genuinely recursive. Guard against inconsistency with a
`//@ check \false;` smoke test that should *fail* to prove.

## 5. Ghost witness to guide the prover

```c
/*@ requires \valid(a + (0..n-1));
    assigns  a[0..n-1];
    ensures  is_permutation{Pre,Here}(a, n);   // user-defined predicate
*/
void reverse(int* a, int n) {
  //@ ghost int steps = 0;
  /*@ loop invariant 0 <= i <= n - 1 - i + 1;
      loop assigns i, a[0..n-1], steps;
      loop variant (n - 1 - i) - i;
  */
  for (int i = 0, j = n - 1; i < j; i++, j--) {
    int t = a[i]; a[i] = a[j]; a[j] = t;
    //@ ghost steps++;
  }
}
```
Ghost state (`steps`) records proof-only information; it must never be read by
non-ghost code.

## 6. MetAcsl — integrity (`\writing`)

"No function except `set_secret` may directly modify `secret`." Documented
(TACAS 2019) form; adjust to your MetAcsl version:

```c
int secret;

/*@ meta only_setter_writes_secret:
      \forall function f; \subset(f, {set_secret}) ==> \writing(f),
      \separated(\written, &secret);
*/
```
`\written` is the location being written; the HILARE forbids any *direct* write
to `&secret` outside `set_secret`. Unlike `assigns`, this is non-transitive — a
function may call `set_secret` without violating it.

## 7. MetAcsl — confidentiality (`\reading`)

"No low-clearance context may read a high-clearance buffer."

```c
/*@ meta no_read_above_clearance:
      \forall function f; \reading(f),
      (current_clearance < SECRET) ==>
        \separated(\read, secret_buf + (0 .. SECRET_LEN - 1));
*/
```
`\read` is the location being read. The premise makes the restriction
*conditional* on dynamic state — another thing `assigns` cannot do.

## 8. MetAcsl — well-formedness everywhere (`strong_invariant`)

```c
/*@ meta status_well_formed:
      \forall function f; \strong_invariant(f),
      \forall integer i; 0 <= i < N ==>
        table[i].status == FREE || table[i].status == BUSY;
*/
```
Holds at every program point of every function — MetAcsl inserts the assertion
after each instruction that could touch a `status` field.

## Where to find large, maintained corpora

- **ACSL by Example** (Fraunhofer FOKUS, Gerlach) — a curated, continuously
  maintained set of STL-style algorithms and data types fully specified in ACSL
  and proved with WP. The single best place to study idiomatic loop invariants,
  axiomatics, and proof structure. See the bibliography for the repo and report.
- **Frama-C book companion** — `git.frama-c.com/pub/frama-c-book-companion`,
  including a `high-level-properties/` directory with MetAcsl examples.
- Real-world annotated code: Contiki (lists, memory allocator, AES-CCM*), Linux
  kernel string functions (VerKer), hypervisor paging (Anaxagoros) — see
  bibliography for exact references.
