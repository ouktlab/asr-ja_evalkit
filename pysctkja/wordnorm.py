import sys
import re
import yaml
from collections import defaultdict


########################
#  Lemma DP
########################
class Cell:
    radix = 100000
    def __init__(self, cost = 0.0, corr = 0, trace = 0, is_cor = False):
        self.cost, self.corr, self.trace, self.is_cor = cost, corr, trace, is_cor
    def pred_c(self, flag, cost_sub):
        return Cell(self.cost + (not flag) * cost_sub, self.corr + flag, 0, flag)
    def pred_d(self, cost_del):
        return Cell(self.cost + cost_del, self.corr, 1, False)
    def pred_i(self, cost_ins):
        return Cell(self.cost + cost_ins, self.corr, 2, False)
    def score(self):
        return self.cost * self.radix - self.corr

def lemma_dp(ref, hyp, cmp_fn=lambda x, y: x == y):
    n_ref, n_hyp = len(ref), len(hyp)
    cost_del, cost_ins, cost_sub = 1, 1, 1

    # initialization
    cell = [[Cell() for j in range(n_hyp+1)] for i in range(n_ref+1)]
    for j in range(n_hyp+1):
        cell[0][j].cost, cell[0][j].trace = j, 2
    for i in range(n_ref+1):
        cell[i][0].cost, cell[i][0].trace = i, 1

    # matching
    for r_idx in range(1, n_ref+1):
        for h_idx in range(1, n_hyp+1):
            c_diag = cell[r_idx-1][h_idx-1].pred_c(cmp_fn(ref[r_idx-1], hyp[h_idx-1]), cost_sub) 
            c_del = cell[r_idx-1][h_idx].pred_d(cost_del)
            c_ins = cell[r_idx][h_idx-1].pred_i(cost_ins)            
            cell[r_idx][h_idx] = sorted([c_diag, c_del, c_ins], key=lambda x: x.score())[0]

    # backtrack
    history = []
    r_idx, h_idx = n_ref, n_hyp
    while r_idx >= 0 and h_idx >= 0:
        id_dir = cell[r_idx][h_idx].trace
        history.append([id_dir, r_idx, h_idx, cell[r_idx][h_idx].is_cor])
        r_idx -= (~id_dir & 0b0010) >> 1
        h_idx -= (~id_dir & 0b0001)

    # align
    history = history[::-1]
    align = [[y[0], x[1], x[2], y[3]] for x, y in zip(history[:-1], history[1:])]
    return align


def adjust_to_reference(lemma_tagger, ref_text, hyp_text):
    #
    ref_lemmas = lemma_tagger(ref_text)
    hyp_lemmas = lemma_tagger(hyp_text)

    ref_adj_text = ''.join([x[1] for x in ref_lemmas])
    #
    alignment = lemma_dp(ref_lemmas, hyp_lemmas, cmp_fn=lambda x, y: x[0] == y[0])

    #
    surfaces = [w[1] for w in hyp_lemmas]
    for x in alignment:
        if x[0] == 0 and x[3] is True: surfaces[x[2]] = ref_lemmas[x[1]][1]
    hyp_adj_text = ''.join(surfaces)

    return ref_adj_text, hyp_adj_text, ref_lemmas, hyp_lemmas

#########
# Lemma Taggers
#########
class FugashiLemmaTaggerV1:
    _pat_lemma = re.compile(r'(.+)-(.+)')
    _skip_tokens = list("。、")

    def __init__(self):
        import fugashi
        self.tagger = fugashi.Tagger()

        import pysctkja.numnorm as numnorm
        self.nnorm = numnorm.KanjiNumConverterV1()

    def __call__(self, text):
        return self.proc(text)

    #
    def concat_numeral(self, words):
        result = []    
        numeral_surface = ''
        for x in words:
            lemma, surface, pos1, pos2 = x
            if pos2 != '数詞':
                if len(numeral_surface) > 0:
                    result.append([numeral_surface, numeral_surface, '名詞', '数詞'])
                    numeral_surface = ''
                result.append(x)
                continue
            numeral_surface += surface
        if len(numeral_surface) > 0:
            result.append([numeral_surface, numeral_surface, '名詞', '数詞'])    
        return result

    def proc(self, text):
        # parsing
        words = [
            [x.feature.lemma, x.surface, x.feature.pos1, x.feature.pos2]
            for x in self.tagger(text)
        ]
        words = self.concat_numeral(words)

        #
        tagged_words = []
        for lemma, surface, pos1, pos2 in words:
            if lemma is None: lemma = surface
            if lemma in self._skip_tokens: continue

            lemma = self._pat_lemma.sub(r'\1', lemma)
            surface = self.nnorm(surface)
            tagged_words.append([lemma, surface])
        
        return tagged_words

###
def usage():
    import argparse
    parser = argparse.ArgumentParser(description='word normalizer')
    parser.add_argument('ref_list', type=argparse.FileType("r", encoding="UTF-8"))
    parser.add_argument('hyp_list', type=argparse.FileType("r", encoding="UTF-8"))
    parser.add_argument('--ref_adj_list', type=argparse.FileType("w", encoding="UTF-8"), default=None)
    parser.add_argument('--hyp_adj_list', type=argparse.FileType("w", encoding="UTF-8"), default=None)
    parser.add_argument('--ref_lemma', type=argparse.FileType("w", encoding="UTF-8"), default=None)
    parser.add_argument('--hyp_lemma', type=argparse.FileType("w", encoding="UTF-8"), default=None)

    args = parser.parse_args()
    return args  

###
def main():
    args = usage()

    wnorm = FugashiLemmaTaggerV1()
    for r_line, h_line in zip(args.ref_list, args.hyp_list):     
        r_line = r_line.strip()
        h_line = h_line.strip()

        try:
            r_key, ref_text = r_line.split('\t', maxsplit=1)
            h_key, hyp_text = h_line.split('\t', maxsplit=1)
        except Exception as e:
            print(f'[ERROR]: {e} at {r_line}, {hline}')
            quit()

        if r_key != h_key:
            print(f'[ERROR]: key difference between reference and hypothesis')
            quit()
        ### 

        ref_adj_text, hyp_adj_text, ref_lemmas, hyp_lemmas = adjust_to_reference(wnorm, ref_text, hyp_text)

        ### 
        if args.ref_adj_list:
            print(f'{r_key}\t{ref_adj_text}', file=args.ref_adj_list)
        if args.hyp_adj_list:
            print(f'{h_key}\t{hyp_adj_text}', file=args.hyp_adj_list)

        if args.ref_lemma:
            print(f'{r_key}\t{ref_lemmas}', file=args.ref_lemma)
        if args.hyp_lemma:
            print(f'{h_key}\t{hyp_lemmas}', file=args.hyp_lemma)

if __name__ == '__main__':
    sys.path.append('..')
    main()
    