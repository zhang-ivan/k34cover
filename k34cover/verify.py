import numpy

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
    assert check == True, f"Check failed for order = {v}!"
    print(check)
    return check


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