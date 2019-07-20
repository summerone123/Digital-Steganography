from PIL import Image
import numpy as np
import math

"""
假设调色板索引为
    0 1 2 3 4 5 6 7
假设亮度序号(Y_index)为
index:  0 1 2 3 4 5 6 7
        2 5 4 1 7 3 6 0
则
# Y_index_inverse
index:  0 1 2 3 4 5 6 7
        7 3 0 5 2 1 6 4

# 例子
载体  [3 0 6 4] ; 待嵌入信息 0110
嵌入：[3 0 6 4]=>[5 7 6 2]=>(by 0110) [4 7 7 2]=>[7 0 0 4]
结果：[3 0 6 4]=>(by 0110)=>[7 0 0 4]
提取：[7 0 0 4]=>[4 7 7 2]=>0110
"""


class GIF_Steg:
    def __init__(self):
        self.im = None

    def load_gif(self, gif_file):
        self.im = Image.open(gif_file)
        self._load_palette()
        self._sort_palette()
        self._load_palette_data()
        self.available_info_len = len(self.palette_data)

    def write(self, info):
        info = self._set_info_len(info)
        self.palette_data = self._write(self.palette_data, info)

    def read(self):
        _len, im_index = self._get_info_len()
        info = self._read(self.palette_data[im_index:im_index + _len])
        return info

    def save(self, filename):
        self.im.save(filename)

    # ==========================================#

    def _load_palette(self):
        self.palette = []
        palette = self.im.palette.palette
        for i in range(int(len(palette) / 3)):
            self.palette.append((palette[3 * i], palette[3 * i + 1], palette[3 * i + 2]))

    def _sort_palette(self):
        f = lambda t: 0.299 * t[0] + 0.587 * t[1] + 0.114 * t[2]
        Y = [f(t) for t in self.palette]
        self.Y_index = np.argsort(Y)
        self.Y_index_inverse = [0] * 256
        for i in range(len(self.Y_index)):
            self.Y_index_inverse[self.Y_index[i]] = i

    def _load_palette_data(self):
        self.palette_data = self.im.getpalette()

    def _set_info_len(self, info):
        l = int(math.log(self.available_info_len, 2)) + 1
        info_len = [0] * l
        _len = len(info)
        info_len[-len(bin(_len)) + 2:] = [int(i) for i in bin(_len)[2:]]
        return info_len + info

    def _get_info_len(self):
        l = int(math.log(self.available_info_len, 2)) + 1
        len_list = []
        for i in range(l):
            _d = self._get_lsb(self.palette_data[i])
            len_list.append(str(_d))
        _len = ''.join(len_list)
        _len = int(_len, 2)
        return _len, l

    def _write(self, palette_data, info):
        for i in range(len(info)):
            Y_index = self.Y_index_inverse[palette_data[i]]
            lower_bit = Y_index % 2
            if lower_bit == info[i]:
                pass
            elif (lower_bit, info[i]) == (0, 1):
                palette_data[i] = self.Y_index[Y_index + 1]
            elif (lower_bit, info[i]) == (1, 0):
                palette_data[i] = self.Y_index[Y_index - 1]
        return palette_data

    def _read(self, palette_data):
        info = []
        for i in range(len(palette_data)):
            info.append(self._get_lsb(palette_data[i]))
        return info

    def _get_lsb(self, _palette_data):
        return self.Y_index_inverse[_palette_data] % 2


if __name__ == "__main__":
    gs = GIF_Steg()
    gs.load_gif('1.gif')
    gs.write([0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1])
    print(gs.read())