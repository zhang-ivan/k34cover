import transversal

M4 = [0, 1, 4, 5, 8, 9, 12, 13, 28, 29]

dict_ur = {52: 13, 53: 13, 56: 13, 57: 13, 60: 13, 61: 13, 64: 16, 65: 16, 68: 17, 69: 17, 72: 17, 73: 17, 76: 17,
           77: 17, 80: 20, 81: 20, 84: 20, 85: 20, 88: 20, 89: 20, 92: 20, 93: 20, 96: 20, 97: 20, 100: 25, 101: 25}

dict_rm = {16: 4, 17: 4, 20: 4, 25: 5, 32: 8, 37: 8, 41: 9}


def u45(u):  # Intermediate design {4,5}-GDD of order u and groups in M4
    assert u % 4 in [0, 1], f'input {u} is not congruent to 0 or 1 (mod 4)!'
    r = dict_ur[u]
    r1 = u - 4 * r
    if u >= 52:
        # trans_blocks = transversal.trans_trim(transversal.trans2(r), 5)
        # truncated_blocks = transversal.truncate(trans_blocks, r1)
        u_design = transversal.truncate(transversal.trans_trim(transversal.trans2(r), 5), r1)
        if r not in M4:
            m = dict_rm[r]
            r2 = r - 4 * m
            # if r2 == m:
            #     r2 = 0
            r_design = transversal.truncate(transversal.trans_trim(transversal.trans2(m), 5), r2)

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
        if r1 not in M4:
            m1 = dict_rm[r1]
            r3 = r1 - 4 * m1
            r1_design = transversal.truncate(transversal.trans_trim(transversal.trans2(m1), 5), r3)

            # fill in r1-hole in u-design...
            r1_design_4 = []
            for block_tmp in r1_design:
                new_block_tmp = tuple(x + 4 * r for x in block_tmp)
                r1_design_4.append(new_block_tmp)
            u_design.extend(r1_design_4)
        design = sorted(u_design)
        print('u45:')
        print(design)
        return design


if __name__ == '__main__':
    u45(101)
