from k34cover.designs import bibd4

from dataclasses import dataclass
from typing import List, Tuple

Block = Tuple[int, ...]      # (a, b, c) for K3, (a, b, c, d) for K4
Edge = Tuple[int, int]       # (u, v) with u < v guaranteed

@dataclass(frozen=True)
class CoverResult:
    v: int
    blocks: List[Block]       # all K3/K4 blocks, normalised (sorted vertices)
    xi: List[Edge]            # edges covered twice (for v ≡ 2,11 mod 12)
    n_k3: int
    n_k4: int


def cover_k3k4(v: int) -> CoverResult:
    cover: List[Block] = []
    xi: List[Edge] = []
    assert v > 6, f'Input v={v} is less than 7!'

    if v % 3 == 1:
        # excess = 0
        if v % 12 in [1, 4]:
            cover = bibd4.bibd4(v)
        else:
            cover = []
        # return cover

    elif v % 3 == 0:
        # excess = 0
        cover = []
        groups = []
        if v % 12 in [0, 3]:
            design = bibd4.bibd4(v + 1)
            # print(design)
            for old_tuple in design:
                new_tuple = [x_ for x_ in old_tuple if x_ != v + 1]
                if len(new_tuple) == 3:
                    groups.append(tuple(sorted(new_tuple)))
                else:
                    cover.append(tuple(sorted(new_tuple)))
            groups = sorted(groups)
            # print(cover)
            # print(groups)
            #  Just in case groups are not perfectly divided...
            indices = []
            for g in groups:
                indices.extend(g)
            # print(indices)
            groups = []
            for i in range(v // 3):
                groups.append((i * 3 + 1, i * 3 + 2, i * 3 + 3))

            relabeled_cover = []
            for tuple_ in cover:
                relabeled_tuple = tuple((indices.index(i_) + 1 for i_ in tuple_))
                # print(relabeled_tuple)
                relabeled_cover.append(relabeled_tuple)
            cover = relabeled_cover
            cover.extend(groups)  # Finally fill in the triples...
            cover = sorted(cover)
            # return cover

    else:
        # excess = 2
        if v % 12 in [2, 11]:
            res_1 = cover_k3k4(v + 1)
            cover_1 = res_1.blocks
            groups = []
            groups.extend([g for g in cover_1 if len(g) == 3])
            # print(groups)
            groups.remove((v - 1, v, v + 1))
            # groups.append((v-1, v))
            blocks = []
            for b in cover_1:
                if len(b) == 4:
                    new_tuple = tuple(x_ for x_ in b if x_ != v + 1)
                    blocks.append(new_tuple)
            cover = [(1, v - 1, v)]
            cover.extend(blocks)
            cover.extend(groups)
            cover = sorted(cover)
            xi = [(1, v - 1), (1, v)]
    # print(cover)
    # print(xi)

    # normalize blocks: sort vertices inside each block
    cover = [tuple(sorted(B)) for B in cover]

    # count K3 vs K4 blocks
    n_k3 = sum(1 for B in cover if len(B) == 3)
    n_k4 = sum(1 for B in cover if len(B) == 4)

    # normalize xi edges as (min, max)
    xi = [(min(a, b), max(a, b)) for (a, b) in xi]


    return CoverResult(
        v=v,
        blocks=cover,
        xi=xi,
        n_k3=n_k3,
        n_k4=n_k4,
    )


if __name__ == '__main__':
    res = cover_k3k4(1201)
    c=res.blocks
    x=res.xi

    print(c)
    print(x)
