def transpose(matrix):
    if not matrix:
        return []
    rows = len(matrix)
    cols = len(matrix[0])
    for row in matrix:
        if len(row) != cols:
            raise ValueError("all rows must have the same length")
    result = [[0 for _ in range(rows)] for _ in range(cols)]
    for i in range(rows):
        for j in range(cols):
            result[j][i] = matrix[i][j]
    return result


def multiply(a, b):
    if not a or not b:
        return []
    a_rows = len(a)
    a_cols = len(a[0])
    b_rows = len(b)
    b_cols = len(b[0])
    if a_cols != b_rows:
        raise ValueError("incompatible matrix dimensions")
    result = [[0 for _ in range(b_cols)] for _ in range(a_rows)]
    for i in range(a_rows):
        for j in range(b_cols):
            cell = 0
            for k in range(a_cols):
                cell += a[i][k] * b[k][j]
            result[i][j] = cell
    return result


if __name__ == "__main__":
    m = [[1, 2, 3], [4, 5, 6]]
    print("transpose:", transpose(m))
    print("multiply:", multiply([[1, 2], [3, 4]], [[5], [6]]))

