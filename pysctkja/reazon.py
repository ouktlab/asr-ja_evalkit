import time
from reazonspeech.espnet.asr import load_model, transcribe, audio_from_path

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
    parser.add_argument('--device', type=str, help='cpu or cuda', default='cuda')

    args = parser.parse_args()
    return args
 
###
def proclist(model, basepath, filelist, outfile):
    fs = 16000
    with open(filelist, "r") as fkey, open(outfile, "w") as rkey:
        for line in fkey:
            key, filepaths = line.strip().split(maxsplit=1)

            result_text = ''
            for filepath in filepaths.split(','):
                audio = audio_from_path(f'{basepath}/{filepath}')
                audio_time = len(audio.waveform)/audio.samplerate
            
                print(f'[LOG]: recognizing -- {key}')
                results = transcribe(model, audio)
                result_text += results.text
            print(f'{key}\t{result_text}', file=rkey, flush=True)

            
def load_offline_model(args):
    model = load_model(args.device)
    return model
            
def main():
    args = usage()
    print(f'[LOG]:', args)
    model = load_offline_model(args)
    print('f[LOG]: finish model loading') 
    proclist(model, args.basepath, args.filelist, args.outfile)

if __name__ == '__main__':
    main()
    
