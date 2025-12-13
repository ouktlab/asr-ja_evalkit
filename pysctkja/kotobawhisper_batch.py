import time
import torch
from transformers import pipeline

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
                result = model(f'{basepath}/{filepath}',
                               return_timestamps=True,
                               #chunk_length_s=30,
                               generate_kwargs=decode_options)
            
                print(f'[LOG]: recognizing -- {key}')                
                result_text += result['text']
            print(f'{key}\t{result_text}', file=rkey, flush=True)
            
def load_offline_model(args):
    model_id = "kotoba-tech/kotoba-whisper-v2.0"
    generate_kwargs = {"language": "ja", "task": "transcribe"}
    pipe = pipeline(
            "automatic-speech-recognition",
            model=model_id,
            #torch_dtype=torch.float32,
            dtype=torch.float32,
            device=args.device,
            model_kwargs={},
        )
    
    return pipe, generate_kwargs
            
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
    
