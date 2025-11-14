import sys
import re
import unicodedata

class CharNormalizerV1:
    ### removal of special tags and characters
    _eos_pat = re.compile(r'<sos/eos>')
    _tag_filler_pat = re.compile(r'\(S:(.+?)\)')
    _num_pat = re.compile(r'([0-9,]+?)')
    _rm_pat = re.compile(r'[『』「」\(\)・…、。？！\?!,;:，]')
    _rmsp_btwn_nonengwrd_pat = re.compile(r'([^a-zA-Z0-9 ]) ([^a-zA-Z0-9 ])')
    _sp_pat = re.compile(r'\s+')

    ### re-composition 
    _rep_pats = {
        '℃':re.compile(r'°C'),
        #'㎡':re.compile(r'm2'),
    }

    def __init__(self):
        pass

    def __call__(self, text):
        return self.proc(text)

    def proc(self, text):
        # 
        text = self._eos_pat.sub(r'', text)
        text = self._tag_filler_pat.sub(lambda m: m[1], text)
        text = self._num_pat.sub(lambda m: m[1].replace(',',''), text)
        text = self._rmsp_btwn_nonengwrd_pat.sub(r'\1\2', text)
        text = self._rmsp_btwn_nonengwrd_pat.sub(r'\1\2', text)
        text = self._rm_pat.sub(' ', text)
        text = unicodedata.normalize('NFKC', text)
        for k, v in self._rep_pats.items():
            text = v.sub(k, text)
        text = self._sp_pat.sub(' ', text)

        # blank
        if len(text) == 0 or text == ' ':
            text = '＊'
    
        return text


###
def main():
    cnorm = CharNormalizerV1()
    for line in sys.stdin:
        line = line.strip()        
        try:
            key, text = line.split(maxsplit=1)
        except Exception as e:
            print(f'[CAUTION]: {line} {e}', file=sys.stderr, flush=True)
            print(f'         : continue by adding a dummy symbol "*"', file=sys.stderr, flush=True)
            key = line
            text = '＊'

        text = cnorm(text)
        print(f'{key}\t{text}', flush=True)


if __name__ == '__main__':
    main()
    
