import time
import whisper

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
    parser.add_argument('--model_name', type=str, help='model name', default='large-v3')
    parser.add_argument('--language', type=str, help='language', default='Japanese')
    parser.add_argument('--device', type=str, help='cpu or cuda', default='cuda')

    args = parser.parse_args()
    return args

###
def proc_keylist(model, decode_options, basepath, filelist, outfile):
    fs = 16000
    with open(filelist, "r") as fkey, open(outfile, "w") as rkey:
        for line in fkey:
            key, filepaths = line.strip().split(maxsplit=1)

            result_text = ''
            for filepath in filepaths.split(','):            
                s = whisper.load_audio(f'{basepath}/{filepath}')
                s = whisper.pad_or_trim(s)
            
                print(f'[LOG]: recognizing -- {key}')
                mel = whisper.log_mel_spectrogram(s, n_mels=128).to(model.device)
                results = whisper.decode(model, mel, decode_options)
                result_text += results.text
            print(f'{key}\t{result_text}', file=rkey, flush=True)

            
def load_offline_model(args):
    decode_options = whisper.DecodingOptions(language=args.language)
    model = whisper.load_model(args.model_name, device=args.device)
    return model, decode_options
            
def main():
    args = usage()
    print(f'[LOG]:', args)
    model, decode_options = load_offline_model(args)
    print('f[LOG]: finish model loading')
    proc_keylist(model, decode_options,
                 args.basepath, args.filelist,
                 args.outfile)


if __name__ == '__main__':
    main()
    
