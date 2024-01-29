import copy
import math

from primefac import primefac

from pg2 import pg2


def trans1(p, alpha, blocks=None, groups=None):  # generate T[q+1,1;q] for q=p**alpha by Lem 3.5
    if groups is None:
        groups = []
    q = p ** alpha
    elm_to_del = q * q + q + 1
    if blocks is None:
        blocks = pg2(p, alpha)
    for block in blocks:
        tuple_tmp = copy.deepcopy(block)
        if elm_to_del in tuple_tmp:
            tuple_tmp = tuple(x for x in tuple_tmp if x != elm_to_del)
            groups.append(tuple_tmp)
            blocks.remove(block)
    # print(blocks)
    # print(groups)

    # Relabelling the elements from 1 to q*(q+1)...

    indices = []
    for group in groups:
        for x in group:
            indices.append(x)
    groups_new = []
    for i in range(q + 1):
        groups_new.append(tuple(range(i * q + 1, (i + 1) * q + 1)))
    groups = groups_new
    dict_tmp = {}
    for i in range(1, q * q + q + 1):
        dict_tmp[i] = indices[i - 1]

    blocks_new = []
    for block in blocks:
        block_tmp = []
        for x in block:
            block_tmp.append(dict_tmp[x])
        blocks_new.append(tuple(sorted(block_tmp)))
    blocks = sorted(blocks_new)
    # print(blocks)
    # print(groups)

    return blocks


def trans_trim(blocks, t=5):  # Trim a T[s,1;r] to get T[t,1;r] for t<=s
    # r = math.sqrt(len(blocks))
    new_blocks = []
    for block in blocks:
        new_block = block[:t]
        new_blocks.append(new_block)
    blocks = new_blocks
    # print(blocks)
    return blocks


def trans_mult(blocks_1, blocks_2, blocks=None):  # multiplication of T[s,1;r1] and T[s,1;r2] gives T[s,1;r1*r2]
    # by Lem 3.4
    if blocks is None:
        blocks = []
    # r1 = math.sqrt(len(blocks_1))
    r2 = math.sqrt(len(blocks_2))
    # s = len(blocks_1[0])
    # print(s)
    for block_1 in blocks_1:
        for block_2 in blocks_2:
            block_tmp = []
            for x in block_2:
                value_tmp = (block_1[math.ceil(x / r2) - 1] - 1) * r2
                if x % r2 == 0:
                    value_tmp += r2
                else:
                    value_tmp += x % r2
                block_tmp.append(int(value_tmp))
            blocks.append(tuple(block_tmp))
    blocks = sorted(blocks)
    # print(blocks)
    return blocks


def prime_factor_mult(n):  # get all prime factors and the corresponding multiplicities of an integer n
    p_factors = list(primefac(n))
    factors = list(set(p_factors))
    mult_dict = {}
    for p in factors:
        mult_dict[p] = p_factors.count(p)
    return mult_dict


def trans2(r):  # get T[s,1;r] for s=1+min(pi**ai) by Thm 3.1
    factors_dict = prime_factor_mult(r)
    min_factor = min(factors_dict, key=lambda factor: factor ** factors_dict[factor])
    # print(min_factor)
    s = min_factor ** factors_dict[min_factor] + 1
    blocks = trans1(min_factor, factors_dict[min_factor])
    del factors_dict[min_factor]
    while bool(factors_dict):
        key_tmp = next(iter(factors_dict))
        deg_tmp = factors_dict[key_tmp]
        blocks_tmp = trans_trim(trans1(key_tmp, deg_tmp), s)
        blocks_updated = trans_mult(blocks, blocks_tmp)
        del factors_dict[key_tmp]
        blocks = blocks_updated
    # print('final:')
    # print(blocks)
    # print(len(blocks))
    return blocks


def truncate(blocks, r1):  # truncate a group from T[s,1;r] to resize it to r1<=r
    new_blocks = []
    r = int(math.sqrt(len(blocks)))
    s = len(blocks[0])
    t = r - r1
    # del_elements = list(range(r * s - t + 1, r * s + 1))
    for block in blocks:
        new_block = tuple(e for e in block if e <= r * s - t)
        new_blocks.append(new_block)
    blocks = new_blocks
    # print(blocks)
    return blocks


if __name__ == '__main__':
    # trans1(3, 2)
    # trans_mult(trans1(2, 1), trans1(2, 1))

    truncate(trans2(20), 10)
