import sys
import re
from collections import defaultdict


def read_from_scorelist(flowin):
    pat_sep = re.compile(f'[|:]')
    rawscores = defaultdict(lambda:defaultdict(lambda:defaultdict(list)))

    for listline in flowin:
        scorefile = listline.strip()

        with open(scorefile) as f:
            ncor = nsub = ndel = nins = nerr = 0
            for line in f:
                if 'Sum ' in line:
                    _,nsent,nent,ncor,nsub,ndel,nins,nerr,nsenterr,*_ = pat_sep.sub('', line).split()

                    nsent = int(nsent)
                    nent = int(nent)
                    ncor = int(ncor)
                    nsub = int(nsub)
                    ndel = int(ndel)
                    nins = int(nins)
                    nerr = int(nerr)
                    nsenterr = int(nsenterr)
                    break

        dirs = scorefile.split('/')
        corpus = dirs[1]

        if 'set-' in dirs[-2]:
            setname = dirs[-2].replace('set-','')
            asrconf = '/'.join(dirs[2:-2])
        else:
            setname = 'basic'
            asrconf = '/'.join(dirs[2:-1])
        
        rawscores[corpus][asrconf][setname] = [nsent, nent, ncor, nsub, ndel, nins, nerr]

    return rawscores


def num2percent_fmt(numscores):
    tmp = [x / numscores[1] for x in numscores][2:]
    return ' '.join([f'{numscores[1]:10d}'] + [f'{x*100:7.3f}' for x in tmp])


def print_table_for_cui(rawscores):
    
    for key_corpus, val_corpus in sorted(rawscores.items(), key=lambda item: item[0]):
        print('--------------------------------------------------------------')
        print(key_corpus)

        for key_asrconf, val_asrconf in sorted(val_corpus.items(), key=lambda item: item[0]):
            print('    ---------------------')
            print('       ', key_asrconf)
            print('    ---------------------')
            print('    Set                  # Cnt    Corr     Sub     Del     Ins     Err')
            print('    ---------------------')
            sum_scores = [0]*7
            for key_setname, val_scores in sorted(val_asrconf.items(), key=lambda item: item[0]):
                sum_scores = [sum_scores[i] + x for i, x in enumerate(val_scores)]
                val_percent = num2percent_fmt(val_scores)
                print(f'    {key_setname:15s}', val_percent)
            sum_percent = num2percent_fmt(sum_scores)
            print('    ---------------------')
            print(f'    {"Sum":14s} ', sum_percent)
            print('    ---------------------')


def print_table_for_sumcer(rawscores, path_to_tag):
    table = defaultdict(lambda: defaultdict(float))
    chars = {}

    corpus_set = set()
    for key_corpus, val_corpus in sorted(rawscores.items(), key=lambda item: item[0]):
        corpus_set.add(key_corpus)
        for key_asrconf, val_asrconf in sorted(val_corpus.items(), key=lambda item: item[0]):
            sum_scores = [0]*7
            for key_setname, val_scores in sorted(val_asrconf.items(), key=lambda item: item[0]):
                sum_scores = [sum_scores[i] + x for i, x in enumerate(val_scores)]
            if (tag := path_to_tag.get(key_asrconf)) is None:
                continue

            table[tag][key_corpus] = sum_scores[-1]/sum_scores[1]*100
            chars[key_corpus] = sum_scores[1]

    #####
    for tag, v in sorted(table.items()):
        print(f'{"| CER (%)   ":26s}',end='|')
        for name in sorted(corpus_set):
            print(f'{name:>10s} ', end='|')
        print('')
        print(f'{"| --- ":26s}',end='|')
        for name in sorted(corpus_set):
            print(f'{" ---:":11s}', end='|')
        print('')
        break

    for tag, v in sorted(table.items()):
        print(f'| {tag:24s}', end='|')
        for corpus in sorted(corpus_set):
            print(f'{table[tag][corpus]:10.2f} ', end='|')
        print('')

    print('')

    
    ###
    for tag, v in sorted(table.items()):
        print(f'{"|   ":26s}',end='|')
        for name in sorted(corpus_set):
            print(f'{name:>10s} ', end='|')
        print('')
        print(f'{"| --- ":26s}',end='|')
        for name in sorted(corpus_set):
            print(f'{" ---:":11s}', end='|')
        print('')
        break
    print(f'{"| # of characters":26s}',end='|')
    for k, v in sorted(chars.items()):
        print(f'{v:>10d} ', end='|')
    print('')

def read_tabletag(fin):
    tag = {}
    for line in fin:
        line = line.strip()
        v, k = line.split('\t', maxsplit=1)
        tag[k] = v
    return tag
#
def usage():
    import argparse
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('mode', help='')
    parser.add_argument('--flowin', type=argparse.FileType("r", encoding="UTF-8"), default=sys.stdin)
    parser.add_argument('--tagfile', type=argparse.FileType("r", encoding="UTF-8"))
    args = parser.parse_args()
    return args


def main():
    args = usage()    
    rawscores = read_from_scorelist(args.flowin)

    if args.mode == 'cui':
        print_table_for_cui(rawscores)
    if args.mode == 'sumcer':
        path_to_tag = read_tabletag(args.tagfile)
        print_table_for_sumcer(rawscores, path_to_tag)
    
if __name__ == "__main__":
    main()
