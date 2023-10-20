import numpy as np 
from scipy.optimize import linear_sum_assignment

def Hungarian(M, mode='min'):
    A = None

    if mode == 'max':
        _max = M.max()
        A = -M + _max
    elif mode == 'min':
        A = np.array(M, copy=True)

    return linear_sum_assignment(A)

def Greedy(M):
    n = M.shape[0]
    row_ind = np.arange(n)
    col_ind = np.empty(n, dtype=np.int32)
    selected = np.zeros(n)

    for i in range(n):
        _max = -1
        _ind = -1
        for j in range(n):
            if not selected[j] and M[i][j] > _max:
                _max = M[i][j]
                _ind = j
        selected[_ind] = 1
        col_ind[i] = _ind
    return (row_ind, col_ind)

def Thrifty(M):
    n = M.shape[0]
    _max = M.max()
    row_ind = np.arange(n)
    col_ind = np.empty(n, dtype=np.int32)
    selected = np.zeros(n)

    for i in range(n):
        _min = _max + 1
        _ind = -1
        for j in range(n):
            if not selected[j] and M[i][j] < _min:
                _min = M[i][j]
                _ind = j
        selected[_ind] = 1
        col_ind[i] = _ind
    return (row_ind, col_ind)

def GreedyThrifty(M, p=0.5):
    n = M.shape[0]
    n1 = int(n*p)
    row_ind = np.arange(n)
    col_ind = np.empty(n, dtype=np.int32)
    selected = np.zeros(n)
    
    for i in range(n1):
        _max = -1
        _ind = -1
        for j in range(n):
            if not selected[j] and M[i][j] > _max:
                _max = M[i][j]
                _ind = j
        selected[_ind] = 1
        col_ind[i] = _ind
    
    _max = M.max()
    for i in range(n1, n):
        _min = _max + 1
        _ind = -1
        for j in range(n):
            if not selected[j] and M[i][j] < _min:
                _min = M[i][j]
                _ind = j
        selected[_ind] = 1
        col_ind[i] = _ind

    return (row_ind, col_ind)

def ThriftyGreedy(M, p=0.5):
    n = M.shape[0]
    n1 = int(n*p)
    row_ind = np.arange(n)
    col_ind = np.empty(n, dtype=np.int32)
    selected = np.zeros(n)
    
    _max = M.max()
    for i in range(n1):
        _min = _max + 1
        _ind = -1
        for j in range(n):
            if not selected[j] and M[i][j] < _min:
                _min = M[i][j]
                _ind = j
        selected[_ind] = 1
        col_ind[i] = _ind

    for i in range(n1, n):
        _max = -1
        _ind = -1
        for j in range(n):
            if not selected[j] and M[i][j] > _max:
                _max = M[i][j]
                _ind = j
        selected[_ind] = 1
        col_ind[i] = _ind
    

    return (row_ind, col_ind)


if __name__ == "__main__":
    pass
