import sys
import re

###
class RuleBasedNormalizer:
    def __init__(self, rulefile):
        self.load_rule(rulefile)

    def __call__(self, text):
        return self.proc(text)

    def load_rule(self, dictfile):
        self.patterns = []
        with open(dictfile) as f:
            for line in f:
                line = line.strip()
                if '#' in line:
                    continue
                if len(line) == 0:
                    continue
                
                try:
                    word_to, str_regex = line.split('\t', maxsplit=1)
                    self.patterns.append((word_to, re.compile(rf'{str_regex}')))
                except:
                    try:
                        word_to, str_regex = line.split(maxsplit=1)
                        self.patterns.append((word_to, re.compile(rf'{str_regex}')))
                    except Exception as e:
                        print(f'[ERROR]: {e}', file=sys.stderr)
                        print(f'       : {line}. skippped.', file=sys.stderr)
    
    def proc(self, text):
        for x, y in self.patterns:
            text = y.sub(x, text) 
        return text

###
def usage():
    import argparse
    parser = argparse.ArgumentParser(description='rule-based text normalizer')
    parser.add_argument('rulefile', help='')
    args = parser.parse_args()
    return args    

###
def main():
    args = usage()
    rnorm = RuleBasedNormalizer(args.rulefile)
    for line in sys.stdin:
        key, text = line.strip().split('\t', maxsplit=1)
        text = rnorm(text)
        print(f'{key}\t{text}', flush=True)

if __name__ == '__main__':
    main()
    
