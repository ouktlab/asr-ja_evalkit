import sys

def load_kvfile(kvfile):
    kvlist = {}
    with open(kvfile) as f:
        for line in f:
            try:
                key, text = line.split('\t', maxsplit=1)
            except:
                try:
                    key, text = line.split(maxsplit=1)
                except Exception as e:
                    print(f'[CAUTION]: {line} {e}', file=sys.stderr, flush=True)
                    print(f'         : continue by adding dummy symbol "*"', file=sys.stderr, flush=True)
                    key = line
                    text = '＊'      
            kvlist[key] = text
    return kvlist

def save_kvfile(kvfile, data):
    with open(kvfile, 'w') as f:
        for key, text in data.items():
            print(f'{key}\t{text}', file=f, flush=True)

def save_trnfile(kvfile, data):
    with open(kvfile, 'w') as f:
        for key, text in data.items():
            print(f'{text}\t({key})', file=f, flush=True)

class PreProcessor:
    def __init__(self, charnormalizer, rulefile):
        import pysctkja.charnorm as charnorm
        import pysctkja.rulenorm as rulenorm

        self.pipeline = []

        # character normalizer
        if charnormalizer == 'charnorm-v1':
            print(f'[LOG]: load "CharNormalizerV1()" in PreProcessor')
            self.pipeline.append(charnorm.CharNormalizerV1())
        
        # rule-based pre-normalizer
        if rulefile is not None:
            print(f'[LOG]: load "RuleBasedNormalizer({rulefile})" in PreProcessor')
            self.pipeline.append(rulenorm.RuleBasedNormalizer(rulefile))

    def __call__(self, data):
        return self.proc(data)

    def proc(self, data):
        for proc in self.pipeline:
            data = proc(data)
        return data

class LemmaProcessor:
    def __init__(self, tagger):
        if tagger == 'fugashi-v1':
            from pysctkja.wordnorm import FugashiLemmaTaggerV1
            print(f'[LOG]: load "FugashiLemmaTaggerV1()"')
            self.tagger = FugashiLemmaTaggerV1()
        else:
            print(f'[ERROR]: unknown tagger {args.tagger}')
            quit()

    def __call__(self, data):
        return self.tagger(data)

class PostProcessor:
    def __init__(self, trnfmtr='char', rulefile=None):
        import pysctkja.trnformatter as trnformatter
        import pysctkja.rulenorm as rulenorm
        self.pipeline = []

        # rule-based post-normalizer
        if rulefile is not None:
            print(f'[LOG]: load "RuleBasedNormalizer({rulefile})" in PostProcessor')
            self.pipeline.append(rulenorm.RuleNormalizer(rulefile))

        # 
        if trnfmtr == 'char':
            print(f'[LOG]: load "CharFormatter()" in PostProcessor')
            self.pipeline.append(trnformatter.CharFormatter())

    def __call__(self, data):
        return self.proc(data)

    def proc(self, data):
        for proc in self.pipeline:
            data = proc(data)
        return data

def process_foreach(ref_keytext, hyp_keytext, preproc, lemproc, postproc):
    from types import SimpleNamespace
    ref = SimpleNamespace(pre_texts={}, adj_texts={}, lemmas={}, post_texts={})
    hyp = SimpleNamespace(pre_texts={}, adj_texts={}, lemmas={}, post_texts={})

    from pysctkja.wordnorm import adjust_to_reference

    for key, hyp_raw_text in hyp_keytext.items():
        if (ref_raw_text := ref_keytext.get(key)) is None:
            print(f'[ERROR]: "{key}" is not found in reference.')
            quit()

        # from raw text to filtered text
        ref_pre_text = preproc(ref_raw_text)
        hyp_pre_text = preproc(hyp_raw_text)

        ref.pre_texts[key] = ref_pre_text        
        hyp.pre_texts[key] = hyp_pre_text        

        # from filtered text to word list
        ref_adj_text, hyp_adj_text, ref_lemma, hyp_lemma = adjust_to_reference(lemproc, ref_pre_text, hyp_pre_text)

        ref.adj_texts[key] = ref_adj_text
        hyp.adj_texts[key] = hyp_adj_text
        ref.lemmas[key] = ref_lemma
        hyp.lemmas[key] = hyp_lemma

        # from word list to token-space-splitted text
        ref_post_text = postproc(ref_adj_text)
        hyp_post_text = postproc(hyp_adj_text)

        ref.post_texts[key] = ref_post_text
        hyp.post_texts[key] = hyp_post_text

    return ref, hyp

def process_foreach_wotagger(ref_keytext, hyp_keytext, preproc, postproc):
    from types import SimpleNamespace
    ref = SimpleNamespace(pre_texts={}, post_texts={})
    hyp = SimpleNamespace(pre_texts={}, post_texts={})

    for key, hyp_raw_text in hyp_keytext.items():
        if (ref_raw_text := ref_keytext.get(key)) is None:
            print(f'[ERROR]: "{key}" is not found in reference.')
            quit()

        # from raw text to filtered text
        ref_pre_text = preproc(ref_raw_text)
        hyp_pre_text = preproc(hyp_raw_text)

        ref.pre_texts[key] = ref_pre_text        
        hyp.pre_texts[key] = hyp_pre_text        

        # from word list to token-space-splitted text
        ref_post_text = postproc(ref_pre_text)
        hyp_post_text = postproc(hyp_pre_text)

        ref.post_texts[key] = ref_post_text
        hyp.post_texts[key] = hyp_post_text

    return ref, hyp

#
def run_sctk(ref_trn, hyp_trn, scorefile):
    import subprocess, sys
    with open(scorefile, 'w', encoding="UTF-8") as f:
        subprocess.run([
            'sctk', 'sclite', '-r', ref_trn, 'trn', '-h', hyp_trn, 'trn',
            '-i', 'rm', '-o', 'all', 'stdout'
            ], stdout=f)
    
# 
def usage_pyscliteja():
    import argparse
    parser = argparse.ArgumentParser(description='ASR-ja evaluation script. "sctk" command is required.')
    parser.add_argument('ref_list', help='[IN]: Reference list file (key-value pairs with "TAB" delimitor)')
    parser.add_argument('hyp_list', help='[IN]: Hypothesis list file (key-value pairs with "TAB" delimitor)')
    parser.add_argument('ref_trn', help='[OUT]: trnfile of reference for sctk input')
    parser.add_argument('hyp_trn', help='[OUT]: trnfile of hypothesis for sctk input')

    # score output
    parser.add_argument('--scorefile', help='[OUT]: scorefile', default=None)

    # pre-processor
    parser.add_argument('--charnorm', help='CharNormalizer', default='charnorm-v1')
    parser.add_argument('--pre_rulefile', help='Rule file for regex-based replacement', default=None)

    # lemma processor
    parser.add_argument('--tagger', help='lemma processor', default='fugashi-v1')
    parser.add_argument('--disable_adjust', help='disable adjustment based on lemma', action='store_true')

    # post-processor
    parser.add_argument('--trnfmt', help='trn file formatter', default='char')
    parser.add_argument('--post_rulefile', help='Rule file for regex-based replacement', default=None)

    # optional output
    parser.add_argument('--ref_pre', help='[OUT]: pre-processed text of referece', type=str, default=None)
    parser.add_argument('--hyp_pre', help='[OUT]: pre-processed text of hypothesis', type=str, default=None)
    parser.add_argument('--ref_adj', help='[OUT]: adjusted text of reference', type=str, default=None)
    parser.add_argument('--hyp_adj', help='[OUT]: adjusted text of hypothesis', type=str, default=None)
    parser.add_argument('--ref_lemma', help='[OUT]: lemma-surface list file', type=str, default=None)
    parser.add_argument('--hyp_lemma', help='[OUT]: lemma-surface list file', type=str, default=None)

    args = parser.parse_args()
    return args    

#
def app_pyscliteja():
    # 
    args = usage_pyscliteja()
    print(f'[LOG]: {args}')

    # setup configurations
    preproc = PreProcessor(args.charnorm, args.pre_rulefile)
    if not args.disable_adjust: lemproc = LemmaProcessor(args.tagger)
    postproc = PostProcessor(args.trnfmt, args.post_rulefile)
    
    # data load
    ref_keytext = load_kvfile(args.ref_list)
    hyp_keytext = load_kvfile(args.hyp_list)
    
    # main process
    if args.disable_adjust:
        args.ref_adj = args.hyp_adj = args.ref_lemma = args.hyp_lemma = None
        ref_data, hyp_data = process_foreach_wotagger(ref_keytext, hyp_keytext, preproc, postproc)
    else:
        ref_data, hyp_data = process_foreach(ref_keytext, hyp_keytext, preproc, lemproc, postproc)

    # main outputs
    save_trnfile(args.ref_trn, ref_data.post_texts)
    save_trnfile(args.hyp_trn, hyp_data.post_texts)

    # optional outputs
    if args.ref_pre: save_kvfile(args.ref_pre, ref_data.pre_texts)
    if args.hyp_pre: save_kvfile(args.hyp_pre, hyp_data.pre_texts)
    if args.ref_adj: save_kvfile(args.ref_adj, ref_data.adj_texts)
    if args.hyp_adj: save_kvfile(args.hyp_adj, hyp_data.adj_texts)
    if args.ref_lemma: save_kvfile(args.ref_lemma, ref_data.lemmas)
    if args.hyp_lemma: save_kvfile(args.hyp_lemma, hyp_data.lemmas)

    # score output
    if args.scorefile: run_sctk(args.ref_trn, args.hyp_trn, args.scorefile)

#####
def usage_preprocess():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--charnorm', help='CharNormalizer', default='charnorm-v1')
    parser.add_argument('--pre_rulefile', help='Rule file for regex-based replacement', default=None)
    args = parser.parse_args()
    return args

def app_preprocess():
    # 
    args = usage_preprocess()
    preproc = PreProcessor(args.charnorm, args.pre_rulefile)

    #
    for line in sys.stdin:
        line = line.strip()
        try:
            key, text = line.split('\t', maxsplit=1)
        except Exception as e:
            print(f'[CAUTION]: {line} {e}', file=sys.stderr, flush=True)
            print(f'         : continue by adding dummy symbol "*"', file=sys.stderr, flush=True)
            key = line
            text = '＊'

        text = preproc(text)
        print(f'{key}\t{text}')

#####
def usage_postprocess():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--trnfmt', help='trn file formatter', default='char')
    parser.add_argument('--post_rulefile', help='Rule file for regex-based replacement', default=None)
    args = parser.parse_args()
    return args

def app_postprocess():
    # 
    args = usage_postprocess()
    postproc = PostProcessor(args.trnfmt, args.post_rulefile)

    #
    for line in sys.stdin:
        line = line.strip()
        try:
            key, text = line.split('\t', maxsplit=1)
        except Exception as e:
            print(f'[CAUTION]: {line} {e}', file=sys.stderr, flush=True)
            print(f'         : continue by adding dummy symbol "*"', file=sys.stderr, flush=True)
            key = line
            text = '＊'

        text = postproc(text)
        print(f'{text}\t({key})', file=f, flush=True)


#####
def usage_numnorm():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--numnorm', type=str, default='numnorm-v1')
    args = parser.parse_args()
    return args

def app_numnorm():
    # 
    args = usage_numnorm()

    if args.numnorm == 'numnorm-v1':
        from pysctkja.numnorm import KanjiNumConverterV1
        numnorm = KanjiNumConverterV1()
    else:
        print(f'[ERROR]: unknown normalizer {args.numnorm}')
        quit()

    for line in sys.stdin:
        line = line.strip()
        print(numnorm(line))
