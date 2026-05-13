""  # pycsl
#@ requires 1 == 1
#@ ensures \result == 0 or \result == 1
#@ assigns \nothing
def are_parentheses_balanced(chars: list) -> int:
    # chars encodes brackets as integers: +1 = opening, -1 = closing
    n = len(chars)
    depth = 0
    valid = 1
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant valid == 0 or valid == 1
    #@ loop variant n - i
    while i < n:
        depth += chars[i]
        if depth < 0:
            valid = 0
        if valid == 0:
            i = n
        else:
            i += 1
    if valid == 0:
        return 0
    else:
        if depth == 0:
            return 1
        else:
            return 0


#@ requires n >= 0
#@ requires start >= 0
#@ ensures \result >= 0
#@ assigns \nothing
def bfs_levels(adj: list, n: int, start: int) -> int:
    # Counts reachable hops from start following adj[current] in a chain graph.
    # adj[i] = index of next node; a value >= n means no further neighbour.
    level = 0
    current = start
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop invariant level >= 0
    #@ loop variant n - i
    while i < n:
        if current < n:
            current = adj[current]
            level += 1
        i += 1
    return level


if __name__ == "__main__":
    # {[()]} encoded as: { [ ( ) ] } -> 1 1 1 -1 -1 -1
    print("balanced:", are_parentheses_balanced([1, 1, 1, -1, -1, -1]))
    # Graph A->B->D, C->none, D->none encoded as index chain: A=0,B=1,C=2,D=3
    # adj[0]=1 (A->B), adj[1]=3 (B->D), adj[2]=4 (C->none), adj[3]=4 (D->none)
    adj = [1, 3, 4, 4]
    print("levels:", bfs_levels(adj, 4, 0))