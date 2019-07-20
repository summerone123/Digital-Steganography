import sys
import math
import numpy as np
from PIL import Image
import random


def get_index_matrix(n):
    """
    得到n阶zigzag扫描矩阵
    """
    I = np.array(range(n))
    J = I.reshape(-1, n).T
    M = ((I + J) * (I + J + 2) + (I - J) * (-1) ** (I + J)) / 2
    one_tril = np.triu(np.ones((n, n)))[:, ::-1]
    M = M * one_tril
    M = M + (n ** 2 - 1 - M)[::-1, ::-1] * (1 - one_tril)
    return M.astype(int)


def get_mask(n):
    """
    得到掩码m
    """
    return np.random.randint(low=0, high=2, size=n)


class RS:
    def __init__(self):
        self._region_length = 8
        self.set_parameter()

    def load_bmp(self, bmp_file):
        """
        加载bmp文件
        """
        self.im = Image.open(bmp_file)
        self.w, self.h = self.im.size
        print(">> 加载图片，图片尺寸：", self.w, "x", self.h)

    def set_parameter(self, _region_length=8):
        self._region_length = _region_length
        self._zigzag_index_matrix = get_index_matrix(_region_length)
        self._m = get_mask(_region_length ** 2)

    def analyse(self):
        _rs1 = [0, 0, 0, 0]  # [Rm,Sm,R-m,S-m]
        _rs2 = [0, 0, 0, 0]  # [Rm,Sm,R-m,S-m]
        self._RS_build(_rs1, _rs2)
        _sum = math.ceil(self.w / self._region_length) * math.ceil(self.h / self._region_length)
        _rs1 = [i / _sum for i in _rs1]
        _rs2 = [i / _sum for i in _rs2]
        res = self._get_insert_rate(_rs1, _rs2)
        # print(res) < br >　　　　　　　　　  ############## unfinished

    def get_RS_map(self, n=100):
            """
            得到点集 (嵌入率-RS)
            """
            res = []
            for i in range(n + 1):
                _rs = [0, 0, 0, 0]
                rate = i / n
                self._RS_build_by_rate(_rs, rate)

                print(rate, _rs)
                res.append((rate, _rs))
            return res

        ######################################################

    def _RS_build(self, _rs1, _rs2):
            row = math.ceil(self.w / self._region_length)
            column = math.ceil(self.h / self._region_length)
            for i in range(row):
                for j in range(column):
                    # 从图像取出一块区域，进行zigzag扫描
                    box = np.array([i, j, i + 1, j + 1]) * self._region_length
                    region = self.im.crop(box)
                    region = np.array(region)
                    sequence = self._zigzagScan(region)

                    # 对RS进行统计
                    self._rs_build(sequence, _rs1)

                    # 进行正翻转，得到修改率为1-a/2的序列，对RS进行统计
                    sequence = self._Fm(sequence, np.ones(self._region_length ** 2).astype(int))
                    self._rs_build(sequence, _rs2)

    def _RS_build_by_rate(self, _rs, rate):
            """
            根据嵌入率得到RS的值
            """
            row = math.ceil(self.w / self._region_length)
            column = math.ceil(self.h / self._region_length)
            for i in range(row):
                for j in range(column):
                    # 从图像取出一块区域，进行zigzag扫描
                    box = np.array([i, j, i + 1, j + 1]) * self._region_length
                    region = self.im.crop(box)
                    region = np.array(region)
                    sequence = self._zigzagScan(region)

                    # 以概率rate,嵌入01
                    sequence = self._random_inject(sequence, rate)

                    # 对RS进行统计
                    self._rs_build(sequence, _rs)

    def _zigzagScan(self, m):
            """
            Z字形扫描
            """
            sequence = np.zeros(self._region_length ** 2, ).astype(int)
            for i in range(self._region_length):
                for j in range(self._region_length):
                    index = self._zigzag_index_matrix[i][j]
                    sequence[index] = m[i, j]
            return sequence

    def _random_inject(self, sequence, rate):
            """
            随机嵌入秘密信息，嵌入率rate
            """
            m = np.ceil(np.random.random(self._region_length ** 2) - rate / 2).astype(int)
            return self._Fm(sequence, m)

    def _rs_build(self, sequence, _rs):
            """
            根据sequence修改RS的值
            """
            r1 = self._get_relativity(sequence)
            r2 = self._get_relativity(self._Fm(sequence, self._m))
            r3 = self._get_relativity(self._Fm(sequence, -self._m))

            if r1 < r2:
                _rs[0] += 1
            elif r1 > r2:
                _rs[1] += 1
            if r1 < r3:
                _rs[2] += 1
            elif r1 > r3:
                _rs[3] += 1

    def _get_relativity(self, sequence):
            """
            得到像素相关性
            """
            a = np.abs(np.array(sequence)[1:] - np.array(sequence)[:1])
            return np.sum(a)

    def _Fm(self, sequence, m):
            """
            由m定义的翻转
            """
            # [0,1,-1]
            # (x+0)^0-0,(x+0)^1-0,(x-1)^1+1
            # ((x+a)^b)-a
            a = np.floor(m / 2).astype(int)
            b = np.abs(m).astype(int)
            return ((sequence + a) ^ b) - a

if __name__ == "__main__":
        rs = RS()
        rs.load_bmp("1.bmp")
        # rs.analyse()
        res = rs.get_RS_map()
        import matplotlib.pyplot as plt
        for i in range(4):
            plt.plot([p[0] for p in res], [p[1][i] for p in res], 'ro')
        plt.show()