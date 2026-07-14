import time
import torch
import torchaudio
from huggingface_hub import hf_hub_download
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor

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
def proc_keylist(processor, tokenizer, model, basepath, filelist, outfile, device):
    
    with open(filelist, "r") as fkey, open(outfile, "w") as rkey:
        for line in fkey:
            key, filepaths = line.strip().split(maxsplit=1)

            result_text = ''
            for filepath in filepaths.split(','):
                wav, sr = torchaudio.load(f'{basepath}/{filepath}', normalize=True)
                
                print(f'[LOG]: recognizing -- {key}')
                #user_prompt = "<|audio|>can you transcribe the speech into a written format in Japanese?"
                user_prompt = "<|audio|>can you transcribe the speech into a written format?"
                chat = [
                    {"role": "user", "content": user_prompt},
                ]
                prompt = tokenizer.apply_chat_template(chat, tokenize=False, add_generation_prompt=True)

                # Run the processor + model
                model_inputs = processor(prompt, wav, device=device, return_tensors="pt").to(device)
                model_outputs = model.generate(
                    **model_inputs, max_new_tokens=200, do_sample=False, num_beams=1
                )
                
                # Transformers includes the input IDs in the response
                num_input_tokens = model_inputs["input_ids"].shape[-1]
                new_tokens = model_outputs[0, num_input_tokens:].unsqueeze(0)
                output_text = tokenizer.batch_decode(
                    new_tokens, add_special_tokens=False, skip_special_tokens=True
                )
                result_text += output_text[0]
                
            print(f'{key}\t{result_text}', file=rkey, flush=True)

            
def load_offline_model(args):
    model_name = "ibm-granite/granite-speech-4.1-2b"
    processor = AutoProcessor.from_pretrained(model_name)
    tokenizer = processor.tokenizer
    model = AutoModelForSpeechSeq2Seq.from_pretrained(
        model_name, device_map=args.device, torch_dtype=torch.bfloat16
    )
    
    return processor, tokenizer, model

def main():
    args = usage()
    print(f'[LOG]:', args)
    processor, tokenizer, model = load_offline_model(args)
    
    print('f[LOG]: finish model loading')
    proc_keylist(processor, tokenizer, model, 
                 args.basepath, args.filelist,
                 args.outfile, args.device)


if __name__ == '__main__':
    main()
    
