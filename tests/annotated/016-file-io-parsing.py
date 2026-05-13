""  # pycsl
#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def read_scores_csv(scores: list) -> int:
    n = len(scores)
    total = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        total += scores[i]
        i += 1
    return total


#@ requires 1 == 1
#@ ensures 1 == 1
#@ assigns \nothing
def average_score(scores: list) -> int:
    n = len(scores)
    total = 0
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        total += scores[i]
        i += 1
    if n == 0:
        return 0
    else:
        return total // n


if __name__ == "__main__":
    scores = [10, 14]
    print("total:", read_scores_csv(scores))
    print("average:", average_score(scores))