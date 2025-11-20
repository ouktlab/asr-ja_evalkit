import torchaudio

def usage():
    """
    return
        args: argparse.Namespace
    """
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('model', type=str, help='model file')
    parser.add_argument('filelist', type=str, help='audio filelist')
    parser.add_argument('outfile', type=str, help='result file')
    parser.add_argument('--basedir', type=str, help='basedir of audio file path', default='.')
    parser.add_argument('--device', type=str, help='cpu or cuda', default='cuda')
    parser.add_argument('--nbest', type=int, help='nbest', default=5)
    parser.add_argument('--beam_size', type=int, help='beam size', default=20)
    parser.add_argument('--ctc_weight', type=float, help='nbest', default=0.27)
    parser.add_argument('--lm_weight', type=float, help='lm weight', default=0.3)
    parser.add_argument('--penalty', type=float, help='lm weight', default=0.0)

    args = parser.parse_args()
    return args

#####
#
def proclist(model, filelist, outfile, basedir):
    with open(filelist) as fin, open(outfile, 'w') as fout:
        for line in fin:
            key, filepaths = line.strip().split(maxsplit=1)

            result_text = ''
            for filepath in filepaths.split(','):
                s, fs = torchaudio.load(f'{basedir}/{filepath}')
                s = s.squeeze()
            
                print(f'[LOG]: recognizing -- {key}')
                results = model(s)
                result_text += results[0][0]
                
            print(f'{key}\t{result_text}', file=fout, flush=True)


def load_offline_model(args):
    from espnet2.bin.asr_inference import Speech2Text

    # Load model
    model = Speech2Text.from_pretrained(
        args.model,
        device=args.device,
        token_type='char',
        bpemodel=None,
        maxlenratio=0.0,
        minlenratio=0.0,
        beam_size=args.beam_size,
        nbest=args.nbest,
        ctc_weight=args.ctc_weight,
        lm_weight=args.lm_weight,
        penalty=0.0
    )
    return model

def espnet_main():
    args = usage()
    print(f'[LOG]:', args)
    model = load_offline_model(args)
    print('f[LOG]: finish model loading')    
    proclist(model, args.filelist, args.outfile, args.basedir)
    

if __name__ == '__main__':
    espnet_main()
