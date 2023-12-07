def multiply_matrices(first, second, result, r1, c1, r2, c2):
    for i in range(r1):
        for j in range(c2):
            # Initialize result[i][j] to 0 before summing
            result[i][j] = 0
            for k in range(c1):
                result[i][j] += first[i][k] * second[k][j]

def main(num_mult, mat_dim):
    first = [[i * j * 0.5 for j in range(mat_dim)] for i in range(mat_dim)]
    second = [[(i + j) * 0.5 for j in range(mat_dim)] for i in range(mat_dim)]
    result = [[None] for _ in range(mat_dim)] # All elements in result list replaced with None 

    for _ in range(num_mult):
        # Initialize result with None for each list in range
        for i in range(mat_dim):
            result[i] = [None]*mat_dim
            multiply_matrices(first, second, result, mat_dim, mat_dim, mat_dim, mat_dim)

    print("Result[5][5]:", result[5][5])

if __name__ == "__main__":
    import sys
    num_mult = int(100)
    mat_dim = int(1000)
    main(num_mult, mat_dim)