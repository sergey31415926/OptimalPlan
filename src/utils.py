import numpy as np
import numpy.random as rnd
import matplotlib.pyplot as plt

n, a1, a2, b1, b2 = None, None, None, None, None
K1, K2, Na1, Na2, N1, N2 = None, None, None, None, None, None

def set_seed(s=None):
    if not s:
        rnd.seed(s)
    pass

def set_params(_n, _a1, _a2, _b1, _b2):
    global n, a1, a2, b1, b2
    n = _n
    a1 = _a1
    a2 = _a2
    b1 = _b1
    b2 = _b2
    pass

def get_n():
    global n
    return n

def set_minerals(_K1, _K2, _Na1, _Na2, _N1, _N2):
    global K1, K2, Na1, Na2, N1, N2
    K1 = _K1
    K2 = _K2
    Na1 = _Na1
    Na2 = _Na2
    N1 = _N1
    N2 = _N2
    pass

def rounder(P, r):
    f = lambda x : round(x, r)
    return np.vectorize(f)(P)

def get_matrix():
    P = np.empty((n, n))
    
    P[0] = rnd.uniform(a1, a2, n)
    b = rnd.uniform(b1, b2, (n-1)*n).reshape((n-1, n))
    for i in range(0, n-1):
        P[i+1] = P[i] * b[i]
    
    return P

def add_minerals(P):
    n = P.shape[0]
    """ Minerals, the Braunschweig formula """
    """ Z_ij = P_ij - ( 0.12(K_i + Na_i) + 0.24N_i + 0.48 ) """
    K = rnd.uniform(K1, K2, n)
    Na = rnd.uniform(Na1, Na2, n)
    N = rnd.uniform(N1, N2, n)

    for i in range(n):
        P.T[i] -= 0.12 * (K[i] + Na[i]) + 0.24 * N[i] + 0.48
    
    pos = lambda x : x if x > 0 else 0
    P = np.vectorize(pos)(P)
    
    return P

def tmp_sum(elems):
    n = elems.size
    s = np.empty(n, dtype=elems.dtype)
    s[0] = elems[0]
    for i in range(0, n-1):
        s[i+1] = s[i] + elems[i+1]
    return s

def relative(results):
    mat = np.array([x for x in results.values()]).T
    # print(mat)
    for i in range(mat.shape[0]):
        mat[i] = mat[i] / mat[i].max()
    mat = mat.T
    # print(mat)

    n = 0
    new = {}
    for key in results.keys():
        new[key] = mat[n]
        n +=1

    return new

def Benchmark(matr_generator, matr_count, zero, ops):
    results = {}
    for name, _, _ in ops:
        results[name] = zero

    for matr in matr_generator:
        for name, op, kwarg in ops:
            i, j = op(matr, **kwarg)
            results[name] = results[name] + tmp_sum(matr[i, j])
     
    for name in results:
        results[name] /= matr_count
   
    return results

def Save_to_file(results, path):
    with open(path, 'w+', encoding="UTF-8") as f:
        param_str = ' '.join((
            'n =', str(n), ',',
            'a : [', str(a1), ',', str(a2), '),',
            'b : [', str(b1), ',', str(b2), ')',
            '\nK : [', str(K1), ',', str(K2), '),',
            'Na : [', str(Na1), ',', str(Na2), '),',
            'N : [', str(N1), ',', str(N2), ')\n'
            ))

        line = 64*'-'+'\n'
        f.write(line)
        f.write(param_str)

        tmp = relative(results)
        for name in tmp.keys():
            num_res = str(rounder(tmp[name], 3))
            res = ''.join((name, ' :\n', num_res, '\n'))
            f.write(res)

    pass

def Plot(results):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(6, 7), layout="constrained")
    ax1.ticklabel_format(useOffset=False)
    ax2.ticklabel_format(useOffset=False)

    for name, y in results.items():
        ax1.plot(y, label=name)
    ax1.set_title('S(t) - целевая функция')
    ax1.legend(loc='center right', bbox_to_anchor=(1.5, 0.5))
    ax1.set_xlabel('t - время', fontsize = 10)
    ax1.set_ylabel('S(t)', fontsize = 10)

    for name, y in relative(results).items():
        ax2.plot(y, label=name)
    ax2.set_title('S(t) - относительная целевая функция')
    ax2.set_xlabel('t - время', fontsize = 10)
    ax2.set_ylabel('S(t)', fontsize = 10)

    return fig

if __name__=='__main__':
    pass
