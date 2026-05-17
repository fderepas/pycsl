# Rocq Tactic Deep Reference

## Integer Arithmetic in Why3 Goals

Why3 uses `Numbers.BinNums.Z` (Coq's binary integers) for all integer values. The `%Z` scope annotations are standard.

### Reading Why3-Generated Goals

```coq
(* Integer literals *)
0%Z                    (* zero *)
1%Z                    (* one *)

(* Arithmetic *)
(n + 1%Z)%Z           (* n + 1 *)
(n - i)%Z             (* n - i *)
(n * m)%Z             (* n * m — requires nia for non-linear *)

(* Comparisons — all produce Prop *)
(0%Z <= n)%Z          (* 0 <= n *)
(i < n)%Z             (* i < n *)
~ (i <= n)%Z          (* i > n — negated loop guard *)

(* Conjunctions *)
A /\ B                 (* both must hold *)

(* Equalities in Ensures axioms *)
Axiom Ensures : (s1 = (s + 1%Z)%Z).  (* s1 = s + 1 — from assignment *)
```

### The `generalize` + `lia` Pattern

When `lia` alone can't solve the goal because axioms aren't in the goal context:

```coq
(* Bring specific axioms into the goal as hypotheses *)
generalize Requires H H1 Ensures1. intros. lia.

(* Or bring ALL axioms *)
generalize Requires H H1 H2 LoopInvariant Ensures Ensures1. intros. lia.
```

### Substitution for Equality Axioms

When axioms define variable values (from assignments):

```coq
Axiom Ensures : (s1 = (s + 1%Z)%Z).
Axiom Ensures1 : (i1 = (i + 1%Z)%Z).

(* Substitute s1 and i1 everywhere *)
Proof.
subst.  (* works if Ensures/Ensures1 are equalities *)
lia.
Qed.

(* If subst doesn't work (axioms aren't local hypotheses), use rewrite *)
Proof.
generalize Ensures Ensures1. intros He1 He2. rewrite He1. rewrite He2. lia.
Qed.
```

## Non-Linear Arithmetic

For goals involving multiplication of variables:

```coq
(* nia = non-linear integer arithmetic *)
Require Import Lia.  (* nia is included *)

Theorem vc : (n >= 1)%Z -> (n * n >= 1)%Z.
Proof. intros. nia. Qed.

(* ring = polynomial ring identities *)
Require Import Ring.

Theorem vc : forall a b : Z, ((a + b) * (a + b) = a*a + 2*a*b + b*b)%Z.
Proof. intros. ring. Qed.
```

## Array-Related Goals

Why3 array goals use the `Map` and `Array` theories:

```coq
(* Array length *)
Parameter _arr_length : Numbers.BinNums.Z.
Axiom Requires : (_arr_length = n)%Z.  (* from \length(arr) == n *)

(* Array access — often just integer arithmetic on indices *)
(* Goal: 0 <= i /\ i < _arr_length *)
Proof. generalize H Requires. intros. lia. Qed.
```

## Handling Conjunction Goals

```coq
(* Simple split *)
Theorem vc : A /\ B.
Proof.
split.
- (* prove A *) lia.
- (* prove B *) lia.
Qed.

(* Nested conjunctions *)
Theorem vc : A /\ B /\ C.
Proof.
split; [| split].
- lia.
- lia.
- lia.
Qed.

(* Using intuition to handle propositional structure *)
Theorem vc : A /\ B /\ C.
Proof. intuition lia. Qed.  (* often works for pure arithmetic *)
```

## Decomposing Axiom Conjunctions

```coq
Axiom LoopInvariant : (0%Z <= i)%Z /\ (i <= (n + 1%Z)%Z)%Z.

(* destruct to get both parts *)
Proof.
destruct LoopInvariant as [Hi_lo Hi_hi].
(* Now Hi_lo : 0 <= i and Hi_hi : i <= n + 1 are available *)
lia.
Qed.

(* Or generalize — lia can handle conjunctions in hypotheses *)
Proof.
generalize LoopInvariant. intros [Hi_lo Hi_hi]. lia.
Qed.
```

## Common Why3 Axiom Naming

| Axiom name | Source |
|------------|--------|
| `Requires` | `#@ requires ...` |
| `H`, `H1`, `H2`, ... | Additional requires or from control flow |
| `LoopInvariant` | `#@ loop invariant ...` |
| `LoopInvariant1` | Second loop invariant |
| `Ensures` | From assignment `x = expr` |
| `Ensures1` | Second assignment |

## Debugging Failed Proofs

```coq
(* See what's in scope *)
Proof.
  generalize Requires H H1 LoopInvariant. intros.
  (* Now check the goal state with your eyes *)
  (* If lia doesn't solve it, the axioms are insufficient *)
Abort.

(* Check if a simpler statement is provable *)
Proof.
  assert (Hs: (i >= 0)%Z) by (generalize H; lia).
  (* Build up to the full goal *)
Abort.
```
