# fictional toy code for the example record
def neighbours(A, i):
    return [j for j, a in enumerate(A[i]) if a]
def mean_step(x, A, i):
    return sum(x[j] for j in neighbours(A, i)) / len(neighbours(A, i))
def weighted_step(x, A, i):
    return sum(A[i][j] * x[j] for j in neighbours(A, i)) / sum(A[i])
