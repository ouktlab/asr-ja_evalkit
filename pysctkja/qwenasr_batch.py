import time
import torch

def usage():
    """
    return
        args: argparse.Namespace
    """
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('modelpath', type=str)
    parser.add_argument('filelist', type=str)
    parser.add_argument('outfile', type=str)
    parser.add_argument('--basepath', type=str, default='.')
    parser.add_argument('--device', type=str, help='cpu or cuda', default='cuda')

    args = parser.parse_args()
    return args

###
def proc_keylist(model, basepath, filelist, outfile):
    
    with open(filelist, "r") as fkey, open(outfile, "w") as rkey:
        for line in fkey:
            key, filepaths = line.strip().split(maxsplit=1)

            result_text = ''
            for filepath in filepaths.split(','):
                print(f'[LOG]: recognizing -- {key}')
                results = model.transcribe(
                    audio=f"{basepath}/{filepath}",
                    language="Japanese",
                )
                result_text += results[0].text
            print(f'{key}\t{result_text}', file=rkey, flush=True)

            
def load_offline_model(args):
    from qwen_asr import Qwen3ASRModel
    
    model = Qwen3ASRModel.from_pretrained(
        args.modelpath, #"Qwen/Qwen3-ASR-1.7B",
        dtype=torch.bfloat16,
        device_map=args.device,
        max_inference_batch_size=32, 
        max_new_tokens=1024, 
    )
    
    return model
            
def main():
    args = usage()
    print(f'[LOG]:', args)
    model = load_offline_model(args)
    print('f[LOG]: finish model loading')
    proc_keylist(model, 
                 args.basepath, args.filelist,
                 args.outfile)


if __name__ == '__main__':
    main()
    
