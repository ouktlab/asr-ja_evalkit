import torchaudio
from espnet2.bin.asr_inference import Speech2Text
from transformers import AutoTokenizer, T5ForConditionalGeneration

def usage():
    """
    return
        args: argparse.Namespace
    """
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('sasr_model', type=str, help='model file')
    parser.add_argument('tokenizer', type=str, help='model file')
    parser.add_argument('sct_model', type=str, help='model file')
    parser.add_argument('filelist', type=str, help='audio filelist')
    parser.add_argument('outfile', type=str, help='result file')
    parser.add_argument('sasrfile', type=str, help='result file')
    parser.add_argument('--basedir', type=str, help='basedir of audio file path', default='.')
    parser.add_argument('--device', type=str, help='cpu or cuda', default='cuda')
    parser.add_argument('--nbest', type=int, help='nbest', default=5)
    parser.add_argument('--sasr_beam_size', type=int, help='beam size', default=20)
    parser.add_argument('--ctc_weight', type=float, help='nbest', default=0.21)
    parser.add_argument('--lm_weight', type=float, help='lm weight', default=0.3)
    parser.add_argument('--penalty', type=float, help='lm weight', default=0.0)
    parser.add_argument('--sct_beam_size', type=int, help='beam size', default=15)
    
    args = parser.parse_args()
    return args

#####
#
def proclist(sasr_model, tokenizer, sct_model, filelist, outfile, sasrfile, basedir, sct_beam_size):
    device = next(sct_model.parameters()).device
    
    with open(filelist) as fin, open(outfile, 'w') as fout, open(sasrfile, 'w') as fsasrout:
        for line in fin:
            key, filepaths = line.strip().split()

            sasr_result_text = ''
            sct_result_text = ''
            for filepath in filepaths.split(','):
                s, fs = torchaudio.load(f'{basedir}/{filepath}')
                s = s.squeeze()
            
                print(f'[LOG]: recognizing -- {key}')
                sasr_results = sasr_model(s)
                sasr_result_text += sasr_results[0][0]

                input_text = [sasr_results[0][0]]
                inputs = tokenizer(input_text, return_tensors="pt", padding=True)
                inputs.to(device)
            
                outputs = sct_model.generate(input_ids=inputs.input_ids,
                                             attention_mask=inputs.attention_mask,
                                             max_length=len(input_text[0])+64,
                                             return_dict_in_generate=True,
                                             num_beams=sct_beam_size,
                                             length_penalty=0.0,
                                             do_sample=False, output_logits=False, 
                                             output_scores=True)
            
                for i, output_ids in enumerate(outputs['sequences']):
                    sct_result = tokenizer.decode(output_ids, skip_special_tokens=True)
                    break
            
                sct_result_text += sct_result
                
            print(f'{key}\t{sasr_result_text}', file=fsasrout, flush=True)
            print(f'{key}\t{sct_result_text}', file=fout, flush=True)


def load_offline_model(args):
    # Load model
    sasr_model = Speech2Text.from_pretrained(
        args.sasr_model,
        device=args.device,
        token_type='char',
        bpemodel=None,
        maxlenratio=0.0,
        minlenratio=0.0,
        beam_size=args.sasr_beam_size,
        nbest=args.nbest,
        ctc_weight=args.ctc_weight,
        lm_weight=args.lm_weight,
        penalty=0.0
    )

    tokenizer = AutoTokenizer.from_pretrained(args.tokenizer, 
                                              trust_remote_code=True)
    sct_model = T5ForConditionalGeneration.from_pretrained(args.sct_model)
    sct_model.to(args.device)
    sct_model.eval()

    return sasr_model, tokenizer, sct_model

def main():
    args = usage()
    print(f'[LOG]:', args)
    sasr_model, tokenizer, sct_model = load_offline_model(args)
    print('f[LOG]: finish model loading')    
    proclist(sasr_model, tokenizer, sct_model, args.filelist, args.outfile, args.sasrfile, args.basedir, args.sct_beam_size)    

if __name__ == '__main__':
    main()
