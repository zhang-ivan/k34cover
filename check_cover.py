import sys

import numpy
import k3k4cover

numpy.set_printoptions(threshold=sys.maxsize)


def k3k4cover_checker(v, input_design_):
    # Check whether a design is the minimum cover of Kv by K3 and K4 with minimum excess
    adjacency = numpy.zeros((v, v))

    for tuple_ in input_design_:
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
            l_ = block[3]
            adjacency[i - 1][j - 1] += 1
            adjacency[j - 1][i - 1] += 1
            adjacency[i - 1][k - 1] += 1
            adjacency[k - 1][i - 1] += 1
            adjacency[j - 1][k - 1] += 1
            adjacency[k - 1][j - 1] += 1
            adjacency[i - 1][l_ - 1] += 1
            adjacency[l_ - 1][i - 1] += 1
            adjacency[j - 1][l_ - 1] += 1
            adjacency[l_ - 1][j - 1] += 1
            adjacency[k - 1][l_ - 1] += 1
            adjacency[l_ - 1][k - 1] += 1
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
    # difference = adjacency - theoretical
    # print(difference)
    check = numpy.array_equal(adjacency, theoretical)
    print(check)


def sort_lost_of_tuples(original_cover):
    cover_tmp_1 = []
    for tuple_1 in original_cover:
        tuple_tmp_1 = tuple(sorted(tuple_1))
        cover_tmp_1.append(tuple_tmp_1)
    cover = sorted(cover_tmp_1, key=lambda x_: (len(x_), x_))
    return cover


def count_k3_k4(cover):  # Input a sorted cover!
    l_ = len(cover)
    i = 0
    while len(cover[i]) == 3:
        i += 1
    alpha = i
    beta = l_ - alpha
    return alpha, beta


def assign_diagonal(cover, order_):  # Input a sorted cover!
    assigned_dict = {}
    l_ = len(cover)
    occurrence_ = []
    for i in range(1, order_ + 1):
        occurrence_.append([i])
        for j in range(l_):
            if i in cover[j]:
                occurrence_[i - 1].append(cover[j])
    while len(occurrence_) > 0:
        occurrence_ = sorted(occurrence_, key=lambda x: len(x))
        i_ = occurrence_[0][0]
        assigned_dict[i_] = occurrence_[0][1]
        for row in occurrence_:
            try:
                row.remove(assigned_dict[i_])
            except ValueError:
                pass
        del occurrence_[0]
    assigned_dict = dict(sorted(assigned_dict.items()))
    return assigned_dict


if __name__ == '__main__':
    for order in range(227, 1201):
        if order % 12 in [0, 1, 2, 3, 4, 11]:
            print('------------')
            print(f'order = {order}')
            design_, xi = k3k4cover.cover_k3k4(order)
            design = sort_lost_of_tuples(design_)
            # print(f'design for K-{order}:')
            # print(design)
            print(f'excess for K-{order}:')
            print(xi)
            count_k3, count_k4 = count_k3_k4(design)
            print(f'number of triples: {count_k3}')
            print(f'number of quadruples: {count_k4}')
            # print('Assigning diagonal:')
            # dict_diagonal = assign_diagonal(design, order)
            # print(dict_diagonal)
            print(f'check result for K-{order}:')
            k3k4cover_checker(order, design)

    # order = 1201
    # design_, xi = k3k4cover.cover_k3k4(order)
    # design = sort_lost_of_tuples(design_)
    # print(f'design for K-{order}:')
    # # print(design)
    # print(f'excess for K-{order}:')
    # print(xi)
    # count_k3, count_k4 = count_k3_k4(design)
    # print(f'number of triples: {count_k3}')
    # print(f'number of quadruples: {count_k4}')
    # print('Assigning diagonal:')
    # dict_diagonal = assign_diagonal(design, order)
    # print(dict_diagonal)
    # print(f'check result for K-{order}:')
    # k3k4cover_checker(order, design)
