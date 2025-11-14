import sys
import re

if len(sys.argv) < 2:
    print('usage: key-path key-rawtext')
    quit()

[pathfile, textfile] = sys.argv[1:3]

pat_rm = re.compile(r'\[<unk>\]')
pat_unk = re.compile(r'\[<unk>/(.+?)\]')
pat_tag = re.compile(r'\[(.+?)/(.+?)\]')

####
with open(pathfile, 'w') as pathf, open(textfile, 'w') as textf:
    for line in sys.stdin:
        wavpath, text = line.strip().split(maxsplit=1)

        m = re.match(r'(.*)_(.*).wav', wavpath)
        
        spkrid = m.group(1).replace('-', '_')
        others = m.group(2)
        
        key = spkrid + '-' + others

        text_wotag = pat_rm.sub(r'', text)
        text_wotag = pat_unk.sub(r'\1', text_wotag)
        text_wotag = pat_tag.sub(r'\1', text_wotag)

        print(f'{key}\t{text_wotag}', file=textf)
        print(f'{key}\tver1.0/01_jpn/segmented/WAVE/{wavpath}', file=pathf)
        

    
