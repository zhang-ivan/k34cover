import transversal
import galois

M4 = [0, 1, 4, 5, 8, 9, 12, 13, 28, 29]

dict_ur = {0: 0, 1: 0, 4: 0, 5: 0, 8: 0, 9: 0, 12: 0, 13: 0, 16: 4, 17: 4, 20: 4, 21: 5, 24: 5, 25: 5, 28: 0, 29: 0,
           32: 8, 33: 8, 36: 8, 37: 8, 40: 8, 41: 9, 44: 9, 45: 9, 48: 12, 49: 12, 52: 13, 53: 13, 56: 13, 57: 13,
           60: 13, 61: 13, 64: 16, 65: 16, 68: 17, 69: 17, 72: 17, 73: 17, 76: 17, 77: 17, 80: 20, 81: 20, 84: 20,
           85: 20, 88: 20, 89: 20, 92: 20, 93: 20, 96: 20, 97: 20, 100: 25, 101: 25}

# dict_rm = {16: 4, 17: 4, 20: 4, 25: 5, 32: 8, 37: 8, 41: 9}

gdd4_3_4 = [(1, 4, 9, 11), (1, 5, 8, 12), (1, 6, 7, 10), (2, 4, 7, 12), (2, 5, 9, 10), (2, 6, 8, 11), (3, 4, 8, 10),
            (3, 5, 7, 11), (3, 6, 9, 12)]
gdd4_3_5 = [(1, 4, 8, 12), (1, 5, 7, 13), (1, 6, 11, 15), (1, 9, 10, 14), (2, 4, 10, 13), (2, 5, 9, 11), (2, 6, 8, 14),
            (2, 7, 12, 15), (3, 4, 9, 15), (3, 5, 12, 14), (3, 6, 7, 10), (3, 8, 11, 13), (4, 7, 11, 14),
            (5, 8, 10, 15), (6, 9, 12, 13)]
bibd4_13 = [(1, 2, 12, 13), (1, 3, 10, 11), (1, 4, 8, 9), (1, 5, 6, 7), (2, 3, 7, 9), (2, 4, 6, 11), (2, 5, 8, 10),
            (3, 4, 5, 13), (3, 6, 8, 12), (4, 7, 10, 12), (5, 9, 11, 12), (6, 9, 10, 13), (7, 8, 11, 13)]


def bibd4_m4(m, blocks=None):  # generate BIBD(3m+1,4,1) by Table 5.3
    assert m in M4, f'input {m} not in M4!'
    if m == 0:
        blocks = []
    elif m == 1:
        blocks = [(1, 2, 3, 4)]
    elif m == 4:
        blocks = bibd4_13
    elif m == 5:
        blocks = [(1, 2, 3, 10), (1, 4, 13, 16), (1, 5, 11, 12), (1, 6, 9, 14), (1, 7, 8, 15), (2, 4, 12, 14),
                  (2, 5, 13, 15), (2, 6, 8, 11), (2, 7, 9, 16), (3, 4, 7, 11), (3, 5, 6, 16), (3, 8, 13, 14),
                  (3, 9, 12, 15), (4, 5, 8, 9), (4, 6, 10, 15), (5, 7, 10, 14), (6, 7, 12, 13), (8, 10, 12, 16),
                  (9, 10, 11, 13), (11, 14, 15, 16)]
    elif m == 8:
        field = galois.GF(25, repr="power", irreducible_poly="x^2-2x-2")
        z = field.primitive_element
        blocks_tmp = []
        for i in range(2):
            for j in range(25):
                if j == 0:
                    tuple_tmp = (1, int(z ** (2 * i)) + 1, int(z ** (2 * i + 8)) + 1, int(z ** (2 * i + 16)) + 1)
                    blocks_tmp.append(tuple(sorted(tuple_tmp)))
                else:
                    tuple_tmp = (int(z ** (j - 1)) + 1, int(z ** (2 * i) + z ** (j - 1)) + 1,
                                 int(z ** (2 * i + 8) + z ** (j - 1)) + 1, int(z ** (2 * i + 16) + z ** (j - 1)) + 1)
                    blocks_tmp.append(tuple(sorted(tuple_tmp)))
        blocks = sorted(blocks_tmp)
    elif m == 9:
        group = galois.GF(3, primitive_element=2, repr="power")
        a = group.primitive_element
        field = galois.GF(9, irreducible_poly="x^2-2x-1", repr="power")
        z = field.primitive_element
        gdd4_3_9 = []
        for i in range(2):
            for j in range(3):
                if j == 0:
                    for k in range(9):
                        if k == 0:
                            tuple_tmp = (3 * int(z ** i) + int(a ** 0) + 1,
                                         3 * int(z ** (i + 4)) + int(a ** 0) + 1,
                                         3 * int(z ** (i + 2)) + int(a ** 1) + 1,
                                         3 * int(z ** (i + 6)) + int(a ** 1) + 1)
                            gdd4_3_9.append(tuple(sorted(tuple_tmp)))
                        else:
                            tuple_tmp = (3 * int(z ** i + z ** (k - 1)) + int(a ** 0) + 1,
                                         3 * int(z ** (i + 4) + z ** (k - 1)) + int(a ** 0) + 1,
                                         3 * int(z ** (i + 2) + z ** (k - 1)) + int(a ** 1) + 1,
                                         3 * int(z ** (i + 6) + z ** (k - 1)) + int(a ** 1) + 1)
                            gdd4_3_9.append(tuple(sorted(tuple_tmp)))
                else:
                    for k in range(9):
                        if k == 0:
                            tuple_tmp = (3 * int(z ** i) + int(a ** 0 + a ** (j - 1)) + 1,
                                         3 * int(z ** (i + 4)) + int(a ** 0 + a ** (j - 1)) + 1,
                                         3 * int(z ** (i + 2)) + int(a ** 1 + a ** (j - 1)) + 1,
                                         3 * int(z ** (i + 6)) + int(a ** 1 + a ** (j - 1)) + 1)
                            gdd4_3_9.append(tuple(sorted(tuple_tmp)))
                        else:
                            tuple_tmp = (3 * int(z ** i + z ** (k - 1)) + int(a ** 0 + a ** (j - 1)) + 1,
                                         3 * int(z ** (i + 4) + z ** (k - 1)) + int(a ** 0 + a ** (j - 1)) + 1,
                                         3 * int(z ** (i + 2) + z ** (k - 1)) + int(a ** 1 + a ** (j - 1)) + 1,
                                         3 * int(z ** (i + 6) + z ** (k - 1)) + int(a ** 1 + a ** (j - 1)) + 1)
                            gdd4_3_9.append(tuple(sorted(tuple_tmp)))
        gdd4_3_9 = sorted(gdd4_3_9)
        blocks = gdd4_3_9
        blocks.extend(
            [(1, 2, 3, 28), (4, 5, 6, 28), (7, 8, 9, 28), (10, 11, 12, 28), (13, 14, 15, 28), (16, 17, 18, 28),
             (19, 20, 21, 28), (22, 23, 24, 28), (25, 26, 27, 28)])
        blocks = sorted(blocks)
    elif m == 12:
        group = galois.GF(37, primitive_element=2, repr="power")
        a = group.primitive_element
        blocks_tmp = []
        for i in range(3):
            for j in range(37):
                if j == 0:
                    tuple_tmp = (1, int(a ** (12 * i)) + 1, int(a ** (12 * i + 11)) + 1, int(a ** (12 * i + 14)) + 1)
                    blocks_tmp.append(tuple(sorted(tuple_tmp)))
                else:
                    tuple_tmp = (j + 1, int(a ** (12 * i) + a ** (j - 1)) + 1,
                                 int(a ** (12 * i + 11) + a ** (j - 1)) + 1, int(a ** (12 * i + 14) + a ** (j - 1)) + 1)
                    blocks_tmp.append(tuple(sorted(tuple_tmp)))
        blocks = sorted(blocks_tmp)
    elif m == 13:
        gdd4_3_39 = []
        for master_block in bibd4_13:
            indices = []
            for el in master_block:
                indices.extend([3 * (el - 1) + 1, 3 * (el - 1) + 2, 3 * el])
            for block in gdd4_3_4:
                block_tmp = []
                for e in block:
                    block_tmp.append(indices[e - 1])
                gdd4_3_39.append(tuple(sorted(block_tmp)))
        blocks = gdd4_3_39
        blocks.extend([(1, 2, 3, 40), (4, 5, 6, 40), (7, 8, 9, 40), (10, 11, 12, 40), (13, 14, 15, 40),
                       (16, 17, 18, 40), (19, 20, 21, 40), (22, 23, 24, 40), (25, 26, 27, 40), (28, 29, 30, 40),
                       (31, 32, 33, 40), (34, 35, 36, 40), (37, 38, 39, 40)])
        blocks = sorted(blocks)

    # print(blocks)
    return blocks


def u45(u, design=None, groups=None):  # Intermediate design {4,5}-GDD of order u and groups in M4
    u = int(u)
    if groups is None:
        groups = []
    if design is None:
        design = []
    assert u % 4 in [0, 1], f'input {u} is not congruent to 0 or 1 (mod 4)!'
    r = dict_ur[int(u)]
    r1 = u - 4 * r
    if u in M4:
        groups.append(tuple(range(1, u + 1)))
    elif u >= 52:
        # trans_blocks = transversal.trans_trim(transversal.trans2(r), 5)
        # truncated_blocks = transversal.truncate(trans_blocks, r1)
        u_design = transversal.truncate(transversal.trans_trim(transversal.trans2(r), 5), r1)
        if r not in M4:
            m = dict_ur[r]
            r2 = r - 4 * m
            # if r2 == m:
            #     r2 = 0
            r_design = transversal.truncate(transversal.trans_trim(transversal.trans2(m), 5), r2)
            # groups.extend([tuple(range(1,m+1)),tuple(range(m+1,2*m+1)),tuple(range(2*m+1,3*m+1)),tuple(range(3*m+1,4*m+1)),tuple(range(4*m+1,r+1))])
            for t in range(4):
                groups.extend([tuple(range(t * r + 1, t * r + m + 1)), tuple(range(t * r + m + 1, t * r + 2 * m + 1)),
                               tuple(range(t * r + 2 * m + 1, t * r + 3 * m + 1)),
                               tuple(range(t * r + 3 * m + 1, t * r + 4 * m + 1))])
            if r2 > 0:
                for t in range(4):
                    groups.append(tuple(range(t * r + 4 * m + 1, t * r + r + 1)))
            # fill in r-holes in u-design...
            r_design_1 = []
            for block_tmp in r_design:
                new_block_tmp = tuple(x + r for x in block_tmp)
                r_design_1.append(new_block_tmp)
            r_design_2 = []
            for block_tmp in r_design_1:
                new_block_tmp = tuple(x + r for x in block_tmp)
                r_design_2.append(new_block_tmp)
            r_design_3 = []
            for block_tmp in r_design_2:
                new_block_tmp = tuple(x + r for x in block_tmp)
                r_design_3.append(new_block_tmp)
            u_design.extend(r_design)
            u_design.extend(r_design_1)
            u_design.extend(r_design_2)
            u_design.extend(r_design_3)
        else:
            groups.extend([tuple(range(1, r + 1)), tuple(range(r + 1, 2 * r + 1)), tuple(range(2 * r + 1, 3 * r + 1)),
                           tuple(range(3 * r + 1, 4 * r + 1))])
        if r1 not in M4:
            m1 = dict_ur[r1]
            r3 = r1 - 4 * m1
            r1_design = transversal.truncate(transversal.trans_trim(transversal.trans2(m1), 5), r3)
            groups.extend([tuple(range(4 * r + 1, 4 * r + m1 + 1)), tuple(range(4 * r + m1 + 1, 4 * r + 2 * m1 + 1)),
                           tuple(range(4 * r + 2 * m1 + 1, 4 * r + 3 * m1 + 1)),
                           tuple(range(4 * r + 3 * m1 + 1, 4 * r + 4 * m1 + 1))])
            if r3 > 0:
                groups.append(tuple(range(4 * r + 4 * m1 + 1, u + 1)))
            # fill in r1-hole in u-design...
            r1_design_4 = []
            for block_tmp in r1_design:
                new_block_tmp = tuple(x + 4 * r for x in block_tmp)
                r1_design_4.append(new_block_tmp)
            u_design.extend(r1_design_4)
        elif r1 > 0:
            groups.extend([tuple(range(4 * int(r) + 1, int(u) + 1))])
        design = sorted(u_design)
        groups = sorted(groups)
        # print('u45:')
        # print(design)
        # print(groups)
    elif u in [16, 17, 20]:
        design = transversal.truncate(transversal.trans1(2, 2), u - 16)
        groups.extend([(1, 2, 3, 4), (5, 6, 7, 8), (9, 10, 11, 12), (13, 14, 15, 16)])
        if u > 16:
            groups.append(tuple(range(17, u + 1)))
    elif u in [21, 24, 25]:
        design = transversal.truncate(transversal.trans_trim(transversal.trans1(5, 1), 5), u - 20)
        groups.extend([(1, 2, 3, 4, 5), (6, 7, 8, 9, 10), (11, 12, 13, 14, 15), (16, 17, 18, 19, 20)])
        groups.append(tuple(range(21, u + 1)))
    elif u in [32, 33, 36, 37, 40]:
        design = transversal.truncate(transversal.trans_trim(transversal.trans1(2, 3), 5), u - 32)
        groups.extend([tuple(range(1, 9)), tuple(range(9, 17)), tuple(range(17, 25)), tuple(range(25, 33))])
        if u > 32:
            groups.append(tuple(range(33, u + 1)))
    elif u in [41, 44, 45]:
        design = transversal.truncate(transversal.trans_trim(transversal.trans1(3, 2), 5), u - 36)
        groups.extend([tuple(range(1, 10)), tuple(range(10, 19)), tuple(range(19, 28)), tuple(range(28, 37))])
        groups.append(tuple(range(37, u + 1)))
    elif u in [48, 49]:
        gdd6_12_6 = []
        for i in range(6):
            for j in range(2):
                block_tmp = [2*i+j+1, 12+2*i+j+1, 24+2*i+j+1, 36+2*i+j+1, 48+2*i+j+1, 60+2*i+j+1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2*i+j+1, 12+2*((i+1)%6)+j+1, 24+2*i+(j+1)%2+1,
                                          36+2*((i+3)%6)+j+1, 48+2*((i+2)%6)+(j+1)%2+1, 60+2*((i+4)%6)+j+1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2*i+j+1, 12+2*((i+2)%6)+j+1, 24+2*((i+2)%6)+(j+1)%2+1,
                                          36+2*i+(j+1)%2+1, 48+2*((i+1)%6)+j+1, 60+2*((i+5)%6)+(j+1)%2+1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2*i+j+1,12+2*((i+3)%6)+j+1,24+2*((i+2)%6)+j+1,
                                          36+2*((i+1)%6)+j+1,48+2*((i+5)%6)+(j+1)%2+1,60+2*((i+4)%6)+(j+1)%2+1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2*i+j+1, 12+2*((i+4)%6)+j+1, 24+2*((i+1)%6)+(j+1)%2+1,
                                          36+2*((i+3)%6)+(j+1)%2+1, 48+2*((i+5)%6)+j+1, 60+2*((i+2)%6)+j+1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2*i+j+1,12+2*((i+5)%6)+j+1,24+2*((i+1)%6)+j+1,
                                          36+2*((i+5)%6)+(j+1)%2+1,48+2*((i+3)%6)+(j+1)%2+1,60+2*((i+1)%6)+(j+1)%2+1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2*i+j+1,12+2*i+(j+1)%2+1,24+2*((i+3)%6)+(j+1)%2+1,
                                          36+2*((i+2)%6)+j+1,48+2*((i+3)%6)+j+1,60+2*((i+2)%6)+(j+1)%2+1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2*i+j+1,12+2*((i+1)%6)+(j+1)%2+1,24+2*((i+5)%6)+(j+1)%2+1,
                                          36+2*((i+2)%6)+(j+1)%2+1,48+2*((i+4)%6)+(j+1)%2+1,60+2*i+(j+1)%2+1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2*i+j+1,12+2*((i+2)%6)+(j+1)%2+1,24+2*((i+4)%6)+j+1,
                                          36+2*((i+5)%6)+j+1,48+2*((i+2)%6)+j+1,60+2*((i+3)%6)+(j+1)%2+1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2*i+j+1,12+2*((i+3)%6)+(j+1)%2+1,24+2*((i+4)%6)+(j+1)%2+1,
                                          36+2*((i+4)%6)+j+1,48+2*((i+1)%6)+(j+1)%2+1,60+2*((i+1)%6)+j+1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2*i+j+1,12+2*((i+4)%6)+(j+1)%2+1,24+2*((i+5)%6)+j+1,
                                          36+2*((i+1)%6)+(j+1)%2+1,48+2*i+(j+1)%2+1,60+2*((i+3)%6)+j+1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                block_tmp = [2*i+j+1,12+2*((i+5)%6)+(j+1)%2+1,24+2*((i+3)%6)+j+1,
                                          36+2*((i+4)%6)+(j+1)%2+1,48+2*((i+4)%6)+j+1,60+2*((i+5)%6)+j+1]
                gdd6_12_6.append(tuple(sorted(block_tmp)))
                gdd6_12_6 = sorted(gdd6_12_6)
        gdd5_12_5 = transversal.trans_trim(gdd6_12_6,5)
        design = transversal.truncate(gdd5_12_5, u-48)
        groups.extend([tuple(range(1,13)),tuple(range(13,25)),tuple(range(25,37)),tuple(range(37,49))])
        if u > 48:
            groups.append(tuple(range(49, u+1)))
        # print(design)
        # print(groups)
    return design, groups


def bibd4(v):  # generate BIBD(v,4,1) by Lem 5.11
    assert v % 12 in [1, 4], f'input {v} is not congruent to 1 or 4 (mod 12)!'
    u = (v - 1) / 3
    u_design, u_groups = u45(u)
    blocks = []
    for master_block in u_design:
        indices = []
        for el in master_block:
            indices.extend([el, el + u, el + 2 * u])
        if len(master_block) == 4:
            for block in gdd4_3_4:
                block_tmp = []
                for e in block:
                    block_tmp.append(int(indices[e - 1]))
                blocks.append(tuple(sorted(block_tmp)))
        elif len(master_block) == 5:
            for block in gdd4_3_5:
                block_tmp = []
                for e in block:
                    block_tmp.append(int(indices[e - 1]))
                blocks.append(tuple(sorted(block_tmp)))
    for group in u_groups:
        m = len(group)
        indices = []
        for el in group:
            indices.extend([el, el + u, el + 2 * u])
        indices.append(v)
        group_design = bibd4_m4(m)
        for block in group_design:
            block_tmp = [int(indices[t - 1]) for t in block]
            blocks.append(tuple(sorted(block_tmp)))

    blocks = sorted(blocks)
    # print('BIBD:')
    # print(blocks)
    return blocks


if __name__ == '__main__':
    bibd4(148)
