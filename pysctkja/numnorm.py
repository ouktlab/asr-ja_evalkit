import sys
import re

class KanjiNumConverterV1:
    # 
    _pat_unit_num = re.compile(r'[〇一二三四五六七八九][〇一二三四五六七八九]+')
    _pat_full_num = re.compile(r'[〇一二三四五六七八九十百千万億兆京零壱弐参肆伍陸漆捌玖拾]+')

    _tbl_numtrans = str.maketrans('零壱弐参肆伍陸漆捌玖拾', '〇一二三四五六七八九十')
    _tbl_kanji2num = {'千':10**3, '百':10**2, '十':10,
                      '〇':0, '一':1, '二':2, '三':3, '四':4, '五':5, '六':6, '七':7, '八':8, '九':9,
                      '万':10**4, '億':10**8, '兆':10**12, '京':10**16}

    # 
    def __init__(self):
        pass

    def __call__(self, surface):
        return self.proc(surface)

    # 
    def unit2num(self, kanjistr):
        kanjistr = kanjistr.translate(self._tbl_numtrans)
        return ''.join([str(self._tbl_kanji2num[x]) for x in list(kanjistr)])

    def full2num(self, kanjistr):
        base_h = base_l = num = 0
        for x in list(kanjistr):
            if x in '万億兆京':
                num += (base_h + base_l) * self._tbl_kanji2num[x]
                base_h = 0
                base_l = 0
            elif x in '十百千':
                base_l = 1 if base_l == 0 else base_l
                base_h += base_l * self._tbl_kanji2num[x]
                base_l = 0
            else:
                base_l = self._tbl_kanji2num[x]
        return num + base_h + base_l

    # 
    def full2mixed(self, kanjistr):
        kanjistr = kanjistr.translate(self._tbl_numtrans)
        base_h = base_l = 0
        num = ''
        for x in list(kanjistr):
            if x in '万億兆京':
                if base_h + base_l != 0:
                    num += str((base_h + base_l)) + x
                else:
                    num += x
                base_h = base_l = 0
            elif x in '十百千':
                base_l = 1 if base_l == 0 else base_l
                base_h += base_l * self._tbl_kanji2num[x]
                base_l = 0
            else:
                base_l = self._tbl_kanji2num[x]
        if base_h + base_l != 0:
            num += str(base_h + base_l)
        if num == '' and base_l == 0:
            num = str(0)
        return num

    def proc(self, surface):
        if self._pat_unit_num.fullmatch(surface) is not None:
            surface = str(self.unit2num(surface))
        elif self._pat_full_num.fullmatch(surface) is not None:
            surface = str(self.full2mixed(surface))   
        return surface

###
def main():
    nnorm = KanjiNumConverterV1()

    for line in sys.stdin:
        line = line.strip()
        print(nnorm(line))

if __name__ == '__main__':
    main()
    