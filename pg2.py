import sympy


def pg2(p, alpha, blocks=None):  # generate PG(2, p**alpha) by Thm 2.1
    if blocks is None:
        blocks = []
    assert sympy.isprime(p), f'Input {p} is not prime!'
    q = p ** alpha
    blocks.append(tuple(range(q * q + 1, q * q + q + 2)))  # a block (q**2+1, ..., q**2+q+1)
    for i in range(q):
        block_tmp1 = [q * q + q + 1]
        for j in range(q):
            block_tmp1.append(i + j * q + 1)
        blocks.append(tuple(sorted(tuple(block_tmp1))))
    for i in range(q):
        block_tmp2 = [q * q + q]
        for j in range(q):
            block_tmp2.append(i * q + j + 1)
        blocks.append(tuple(sorted(tuple(block_tmp2))))
    for i in range(q - 1):
        for j in range(q):
            block_tmp3 = [q * q + i + 1, j * q + 1]
            for k in range(1, q):
                block_tmp3.append(((i + j + k) % q) * q + k + 1)
            blocks.append(tuple(sorted(tuple(block_tmp3))))
    blocks = sorted(blocks)
    # print(blocks)
    return blocks


if __name__ == '__main__':
    pg2_7 = pg2(3, 2)
    # print(len(pg2_7))
