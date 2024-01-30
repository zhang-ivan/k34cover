import sympy
import galois


def pg2(p, alpha, blocks=None):  # generate PG(2, p**alpha) by Thm 2.1
    if blocks is None:
        blocks = []
    assert sympy.isprime(p), f'Input {p} is not prime!'
    q = p ** alpha
    field = galois.GF(q, repr="power")
    z = field.primitive_element
    blocks.append(tuple(range(q * q + 1, q * q + q + 2)))  # a block (q**2+1, ..., q**2+q+1)
    for i in range(q):
        block_tmp1 = [q * q + q + 1]
        for j in range(q):
            block_tmp1.append(i + j * q + 1)
        blocks.append(tuple(sorted(tuple(block_tmp1))))
    # print(blocks)
    for i in range(q):
        block_tmp2 = [q * q + q]
        for j in range(q):
            block_tmp2.append(i * q + j + 1)
        blocks.append(tuple(sorted(tuple(block_tmp2))))
    # print(blocks)
    for i in range(q - 1):
        # block_tmp3 = [q * q + i + 1]
        for j in range(q):
            block_tmp3 = [q * q + i + 1]
            if j == 0:
                block_tmp3.append(1)
                for k in range(q - 1):
                    block_tmp3.append(int(z ** (i + k)) * q + k + 2)
                # print(block_tmp3)
                blocks.append(tuple(sorted(tuple(block_tmp3))))
            else:
                block_tmp3.append(int(z ** (j - 1)) * q + 1)
                for k in range(q - 1):
                    # print([z**i, z**j, z**k])
                    # print([i,j,k])
                    # print(z ** (i +k) + z ** j)
                    block_tmp3.append(int(z ** (i + k) + z ** (j - 1)) * q + k + 2)
                # print(block_tmp3)
                # block_tmp3.append(((i + k) % (q - 1) + j + 1) % q * q + k + 2)
                blocks.append(tuple(sorted(tuple(block_tmp3))))
    # print(blocks)
    blocks = sorted(blocks)
    # print(blocks)
    return blocks


if __name__ == '__main__':
    result = pg2(5,1)
    # print(result)
