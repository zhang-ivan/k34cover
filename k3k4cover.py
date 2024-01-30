import bibd


def cover_k3k4(v, cover=None, xi=None):  # generate minimum K3 and K4 cover of Kv with minimum excess
    # if cover is None:
    #     cover = []
    if xi is None:
        xi = []
    assert v > 6, f'Input {v} less than 7!'
    if v % 3 == 1:
        excess = 0
        if v % 12 in [1, 4]:
            cover = bibd.bibd4(v)
        else:
            cover = []
        # return cover

    elif v % 3 == 0:
        excess = 0
        cover = []
        groups = []
        if v % 12 in [0, 3]:
            design = bibd.bibd4(v + 1)
            for old_tuple in design:
                new_tuple = [x for x in old_tuple if x != v + 1]
                if len(new_tuple) == 3:
                    groups.append(tuple(sorted(new_tuple)))
                else:
                    cover.append(tuple(sorted(new_tuple)))
            groups = sorted(groups)
            #  Just in case groups are not perfectly divided...
            indices = []
            for g in groups:
                indices.extend(g)
            groups = []
            for i in range(v//3):
                groups.append((i*3+1, i*3+2, i*3+3))

            relabeled_cover = []
            for tuple_ in cover:
                relabeled_tuple = tuple(sorted(indices.index(i)+1 for i in tuple_))
                relabeled_cover.append(relabeled_tuple)
            cover = relabeled_cover
            cover.extend(groups)  # Finally fill in the triples...
            cover = sorted(cover)
            # return cover

    else:
        excess = 2
        if v % 12 in [2, 11]:
            cover_1, xi_1 = cover_k3k4(v + 1)
            groups = []
            groups.extend([g for g in cover_1 if len(g) == 3])
            # print(groups)
            groups.remove((v - 1, v, v + 1))
            # groups.append((v-1, v))
            blocks = []
            for b in cover_1:
                if len(b) == 4:
                    new_tuple = tuple(x for x in b if x != v + 1)
                    blocks.append(new_tuple)
            cover = [(1, v - 1, v)]
            cover.extend(blocks)
            cover.extend(groups)
            cover = sorted(cover)
            xi = [(1, v - 1), (1, v)]

    return cover, xi


if __name__ == '__main__':
    c, x = cover_k3k4(74)
    print(c)
    print(x)
