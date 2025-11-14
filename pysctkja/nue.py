import time
import nue_asr

def usage():
    """
    return
        args: argparse.Namespace
    """
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('filelist', type=str)
    parser.add_argument('outfile', type=str)
    parser.add_argument('--basepath', type=str, default='.')
    parser.add_argument('--device', type=str, default='cuda')

    args = parser.parse_args()
    return args

###
def proclist(model, tokenizer, basepath, filelist, outfile):
    fs = 16000
    with open(filelist, "r") as fkey, open(outfile, "w") as rkey:
        for line in fkey:
            key, filepaths = line.strip().split(maxsplit=1)

            result_text = ''
            for filepath in filepaths.split(','):
                print(f'[LOG]: recognizing -- {key}')
                try:
                    results = nue_asr.transcribe(model, tokenizer, f'{basepath}/{filepath}')
                    result_text += results.text
                except:
                    result_text += '。'                    
            print(f'{key}\t{result_text}', file=rkey, flush=True)
            
def load_offline_model(args):
    model = nue_asr.load_model("rinna/nue-asr")
    model.to(args.device)
    tokenizer = nue_asr.load_tokenizer("rinna/nue-asr")
    return model, tokenizer

def main():
    args = usage()
    print(f'[LOG]:', args)
    model, tokenizer = load_offline_model(args)
    print('f[LOG]: finish model loading')
    proclist(model, tokenizer,
             args.basepath, args.filelist,
             args.outfile)


if __name__ == '__main__':
    main()
    
