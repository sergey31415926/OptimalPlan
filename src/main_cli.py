from utils import *
from algorithms import Hungarian, Greedy, Thrifty, GreedyThrifty, ThriftyGreedy


def get_params():
    n = int(input('Размер n = ') or 3)
    a1 = float(input('Нижняя граница а- = ') or 4)
    a2 = float(input('Верхняя граница а+ = ') or 6)
    b1 = float(input('Нижняя граница b- = ') or 0.4)
    b2 = float(input('Верхняя граница  b+ = ') or 0.9)

    set_params(n, a1, a2, b1, b2)
    # utils.set_seed()
    pass

def get_minerals():
    K1 = float(input('Нижняя граница K- = ') or 4.8)
    K2 = float(input('Верхняя граница  K+ = ') or 7)

    Na1 = float(input('Нижняя граница  Na- = ') or 0.2)
    Na2 = float(input('Верхняя граница Na+ = ') or 0.8)

    N1 = float(input('Нижняя граница N- = ') or 1.6)
    N2 = float(input('Верхняя граница N+ = ') or 2.8)

    set_minerals(K1, K2, Na1, Na2, N1, N2)
    pass

def get_alg():
    print("""Выберите алгоритм
        1 - Венгерский
        2 - Жадный
        3 - Бережливый
        4 - Жадно-Бережливый
        5 - Бережливо-Жадный
        Выбор: """, end='')
    c = int(input() or 1)
    algo = None
    match c:
        case 1:
            mode = int(input('Максимум (1) или Минимум (2): ') or 2)
            mode = 'min' if mode == 2 else 'max'
            name = 'Венгерский ' + mode 
            algo = (name, Hungarian, {'mode': mode})
        case 2:
            algo = ('Жадный', Greedy, {})
        case 3:
            algo = ('Бережливый', Thrifty, {})
        case 4:
            p = float(input('Доля жадности :') or 0.5)
            algo = ('Жадно-Бережливый', GreedyThrifty, {'p': p})
        case 5:
            p = float(input('Доля бережливости :') or 0.5)
            algo = ('Бережливо-Жадный', ThriftyGreedy, {'p': p})

    return algo

def Interactive():
    """ Interactive Mode layout """
    P = get_matrix()
    P = rounder(P, 2)
    print('Матрица P без учёта органики:')
    print(P.T)

    P = add_minerals(P)
    P = rounder(P, 2)
    print('С учётом органики:')
    print(P.T)
    
    while True:
        name, alg, kwarg = get_alg()
        
        if kwarg:
            i, j = alg(P, **kwarg)
        else:
            i, j = alg(P)

        """ Show result """
        print('Выбранные элементы (индексы): ', end='') 
        print(j)
        print('  Элементы:', P[i, j])
        
        print('Суммарная стоимость: ', end='')
        _sum = P[i, j].sum()
                
        print(round(_sum, 2))
        if input('Хотите выбрать другой алгоритм? (+/-) ') == '-':
            break

    pass

def Experiment():
    algos = []

    while True:
        algos.append(get_alg())
        if int(input('Начать симуляцию (1) или добавить алгоритм (2):') or 1) == 1:
            break
    
    matr_count = int(input('Кол-во опытов: ') or 3)
    matr = (get_matrix() for i in range(matr_count))
    n = get_n()

    results = Benchmark(matr, matr_count, np.zeros(n), algos)

    # print('\tСредняя динамика целевой функции:')
    # for name, y in results.items():
    #     print('{:16}'.format(name), y)

    fig = plt.figure(figsize=(5, 4))
    ax = fig.add_subplot()

    for name, y in results.items():
        ax.plot(y, label=name)
    ax.legend(loc='best')
    ax.set_xlabel('t - время', fontsize = 10)
    ax.set_ylabel('S(t) - целевая функция', fontsize = 10)
    fig.show()

    pass

while True:
    """ Parameters Layout """
    get_params()
    get_minerals()

    mode = int(input('1 - Эксперимент, 2 - Интерактивный: ') or 1)

    match mode:
        case 1:
            Experiment()
        case 2:
            Interactive()

    if input('Начать заново? (+/-) ') == "-":
        break
    
