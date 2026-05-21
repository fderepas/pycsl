"""Test 0288 — Union-find kernel with path compression"""
# pycsl-flags: --no-proof
_ = 0  # anchor

#@ requires n >= 0
#@ requires \length(parent) >= n
#@ requires 0 <= x and x < n
#@ requires \forall i; 0 <= i and i < n ==> 0 <= parent[i] and parent[i] < n
#@ requires \forall i; 0 <= i and i < n ==> parent[i] <= i
#@ ensures 0 <= \result and \result < n
#@ ensures \result <= x
#@ ensures parent[\result] == \result
#@ ensures parent[x] == \result
#@ ensures \forall i; 0 <= i and i < n ==> 0 <= parent[i] and parent[i] < n
#@ ensures \forall i; 0 <= i and i < n ==> parent[i] <= i
#@ ensures \forall k; 0 <= k and k < \result ==> parent[k] == \old(parent[k])
#@ ensures \forall k; 0 <= k and k < n and \old(parent[k]) == k ==> parent[k] == k
#@ assigns parent[0..n]
def find_compress(parent: list, x: int, n: int) -> int:
    r = x
    #@ loop invariant 0 <= r and r < n
    #@ loop invariant r <= x
    #@ loop invariant \forall i; 0 <= i and i < n ==> parent[i] == \old(parent[i])
    #@ loop variant r
    while parent[r] != r:
        r = parent[r]

    cur = x
    #@ loop invariant 0 <= r and r < n
    #@ loop invariant parent[r] == r
    #@ loop invariant r <= cur and cur < n
    #@ loop invariant \forall i; 0 <= i and i < n ==> 0 <= parent[i] and parent[i] < n
    #@ loop invariant \forall i; 0 <= i and i < n ==> parent[i] <= i
    #@ loop invariant \forall k; 0 <= k and k < r ==> parent[k] == \old(parent[k])
    #@ loop invariant \forall k; 0 <= k and k < n and \old(parent[k]) == k ==> parent[k] == k
    #@ loop variant cur - r
    while parent[cur] != r:
        nxt = parent[cur]
        parent[cur] = r
        cur = nxt
    return r

#@ requires n >= 0
#@ requires \length(parent) >= n
#@ requires 0 <= rx and rx < n
#@ requires 0 <= ry and ry < n
#@ requires \forall i; 0 <= i and i < n ==> 0 <= parent[i] and parent[i] < n
#@ requires \forall i; 0 <= i and i < n ==> parent[i] <= i
#@ requires parent[rx] == rx
#@ requires parent[ry] == ry
#@ ensures 0 <= \result and \result < n
#@ ensures parent[\result] == \result
#@ ensures \result <= rx and \result <= ry
#@ ensures \forall i; 0 <= i and i < n ==> 0 <= parent[i] and parent[i] < n
#@ ensures \forall i; 0 <= i and i < n ==> parent[i] <= i
#@ ensures \forall k; 0 <= k and k < n and k != rx and k != ry ==> parent[k] == \old(parent[k])
#@ assigns parent[0..n]
def link_roots(parent: list, rx: int, ry: int, n: int) -> int:
    if rx < ry:
        parent[ry] = rx
        return rx
    else:
        parent[rx] = ry
        return ry

if __name__ == "__main__":
    parent = [0, 0, 1, 2, 4, 4]
    r3 = find_compress(parent, 3, 6)
    assert r3 == 0
    assert parent == [0, 0, 0, 0, 4, 4]

    r = link_roots(parent, 0, 4, 6)
    assert r == 0
    assert parent == [0, 0, 0, 0, 0, 4]

    r5 = find_compress(parent, 5, 6)
    assert r5 == 0
    assert parent == [0, 0, 0, 0, 0, 0]
    print("PASS")
