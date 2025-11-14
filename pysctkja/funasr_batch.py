import time

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
def proc_keylist(model, basepath, filelist, outfile):
    from funasr.utils.postprocess_utils import rich_transcription_postprocess
    fs = 16000
    import re
    pat_tag = re.compile(r'(<\|.+\|>)')
    
    with open(filelist, "r") as fkey, open(outfile, "w") as rkey:
        for line in fkey:
            key, filepaths = line.strip().split(maxsplit=1)

            result_text = ''
            for filepath in filepaths.split(','):
                print(f'[LOG]: recognizing -- {key}')
                results = model.generate(
                    input=f"{basepath}/{filepath}",
                    cache={},
                    language='ja',
                    use_itn=True,
                    batch_size_s=60,
                    merge_vad=True,
                    merge_length_s=15,
                )
                result_text += pat_tag.sub(r'', results[0]['text'])
            print(f'{key}\t{result_text}', file=rkey, flush=True)

            
def load_offline_model(args):
    from funasr import AutoModel
    model_dir = "iic/SenseVoiceSmall"
    model = AutoModel(
            model=model_dir,
            device=args.device,
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
    
