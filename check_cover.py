import sys

import numpy
import k3k4cover

numpy.set_printoptions(threshold=sys.maxsize)


def k3k4cover_checker(v, design_):  # Check whether a design is the minimum cover of Kv by K3 and K4 with minimum excess
    adjacency = numpy.zeros((v, v))

    for tuple_ in design_:
        block = list(tuple_)
        if len(block) == 3:
            i = block[0]
            j = block[1]
            k = block[2]
            adjacency[i - 1][j - 1] += 1
            adjacency[j - 1][i - 1] += 1
            adjacency[i - 1][k - 1] += 1
            adjacency[k - 1][i - 1] += 1
            adjacency[j - 1][k - 1] += 1
            adjacency[k - 1][j - 1] += 1
        elif len(block) == 4:
            i = block[0]
            j = block[1]
            k = block[2]
            l = block[3]
            adjacency[i - 1][j - 1] += 1
            adjacency[j - 1][i - 1] += 1
            adjacency[i - 1][k - 1] += 1
            adjacency[k - 1][i - 1] += 1
            adjacency[j - 1][k - 1] += 1
            adjacency[k - 1][j - 1] += 1
            adjacency[i - 1][l - 1] += 1
            adjacency[l - 1][i - 1] += 1
            adjacency[j - 1][l - 1] += 1
            adjacency[l - 1][j - 1] += 1
            adjacency[k - 1][l - 1] += 1
            adjacency[l - 1][k - 1] += 1
        else:
            print("ERROR: WRONG BLOCK SIZE!")
    theoretical = numpy.ones((v, v))
    for i in range(v):
        theoretical[i][i] = 0
    if v % 12 in [2, 11]:
        theoretical[0][v - 2] = 2
        theoretical[0][v - 1] = 2
        theoretical[v - 2][0] = 2
        theoretical[v - 1][0] = 2
    difference = adjacency - theoretical
    # print(difference)
    check = numpy.array_equal(adjacency, theoretical)
    print(check)


if __name__ == '__main__':
    for order in range(7, 89):
        if order % 12 in [0,1,2,3,4,11]:
            print('------------')
            print(f'order = {order}')
            design, xi = k3k4cover.cover_k3k4(order)
            print(f'design for K-{order}:')
            print(design)
            print(f'excess for K-{order}:')
            print(xi)
            print(f'check result for K-{order}:')
            k3k4cover_checker(order, design)
