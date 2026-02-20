from datasets import load_dataset
import os
import subprocess

fleurs = load_dataset("google/fleurs", "ja_jp", split="test")

keypathfile = 'list/fleurs_key-path.txt'
keytextfile = 'list/fleurs_key-rawtext.txt'

with open(keypathfile, 'w') as kp, open(keytextfile, 'w') as kt:
    for data in fleurs:
        ###
        _cache_path = data['path']
        dirname, filename = os.path.split(_cache_path)
        cache_path = f'{dirname}/test/{filename}'
        
        local_path =  f'audio/{filename}'
        command = ['ln', '-s', cache_path, local_path]
        subprocess.call(command)

        ###
        key = 'fleurs-' + filename.replace('.wav', '')
        
        text = data['transcription']
        text = text.replace(' ', '')
        
        print(f'{key}\t{local_path}', file=kp)
        print(f'{key}\t{text}', file=kt)

