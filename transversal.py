import copy
import math

from primefac import primefac

from pg2 import pg2


def trans1(p, alpha, blocks=None, groups=None):
    """Lemma 3.5"""
    # generate T[q+1,1;q] for q=p**alpha by Lem 3.5
    if groups is None:
        groups = []
    q = p ** alpha
    elm_to_del = q * q + q + 1
    if blocks is None:
        blocks = pg2(p, alpha)
        # print(blocks)
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
        indices.extend(group)
    # print(indices)
    groups_new = []
    for i in range(q + 1):
        groups_new.append(tuple(range(i * q + 1, (i + 1) * q + 1)))
    groups = groups_new
    # print(groups)
    # dict_tmp = {}
    # for i in range(1, q * q + q + 1):
    #     dict_tmp[i] = indices[i - 1]

    blocks_new = []
    for block in blocks:
        block_tmp = []
        for x in block:
            block_tmp.append(indices.index(x) + 1)
        blocks_new.append(tuple(sorted(block_tmp)))
    # print(blocks_new)
    blocks = sorted(blocks_new)
    # print(blocks)
    # print(groups)

    return blocks


def trans_trim(blocks, t=5):  # Trim a T[s,1;r] to get T[t,1;r] for t<=s
    """Lemma 3.1"""
    # r = math.sqrt(len(blocks))
    new_blocks = []
    for block in blocks:
        new_block = block[:t]
        new_blocks.append(new_block)
    blocks = new_blocks
    # print(blocks)
    return blocks


def trans_mult(blocks_1, blocks_2, blocks=None):  # multiplication of T[s,1;r1] and T[s,1;r2] gives T[s,1;r1*r2]
    """Lemma 3.4"""
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
    """Theorem 3.1"""
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
    if t == 0:
        return blocks
    else:
        # del_elements = list(range(r * s - t + 1, r * s + 1))
        for block in blocks:
            new_block = tuple(e for e in block if e <= r * s - t)
            new_blocks.append(new_block)
        blocks = new_blocks
        # print(blocks)
        return blocks


# def trans_resolve(blocks):  # Form RT[s-1,1;r] from T[s,1;r] by Lem 3.6
#     """Lemma 3.6"""
#     s = len(blocks[0])
#     l_ = len(blocks)
#     r = int(math.sqrt(l_))
#     pc = []
#     for i in range(s):
#         pc.append([])
#     # Assume the groups are well partitioned and ordered in the inputted blocks...
#     for blk_ in blocks:
#         for i in range(s):
#             if r * s - s + 1 + i in blk_:
#                 blk_ = tuple(x for x in blk_ if x != r * s - s + 1 + i)
#                 pc[i].append(blk_)
#     # pc = numpy.array(pc)
#     # print('pc:')
#     # print(pc)
#
#     # Relabelling parallel classes...
#     indices = []
#     for i in range(s - 1):
#         for tpl_ in pc[0]:
#             indices.append(tpl_[i])
#     class_1 = []
#     for i in range(1, r + 1):
#         class_1.append(tuple(range(i, i + (s - 1) * r, r)))
#     new_pc = [class_1]
#     for i in range(1, len(pc)):
#         new_class = []
#         for tuple_ in pc[i]:
#             new_class.append(tuple(indices.index(x) + 1 for x in tuple_))
#         new_pc.append(new_class)
#     return new_pc


if __name__ == '__main__':
    # b = trans1(5, 1)
    # b = trans_trim(b, 5)
    # print(b)
    # classes = trans_resolve(b)
    # print(numpy.array(classes))
    # trans_mult(trans1(2, 1), trans1(2, 1))

    # truncate(trans2(20), 10)
    trans_design = trans2(7)
    print(trans_design)
    trans_design = trans_trim(trans_design)
    print(trans_design)
    trans_design = truncate(trans_design, 3)
    print(trans_design)
