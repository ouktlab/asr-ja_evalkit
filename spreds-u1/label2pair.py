import sys
import re

if len(sys.argv) < 2:
    print('usage: key-path key-rawtext')
    quit()

[pathfile, textfile] = sys.argv[1:3]

    
####
with open(pathfile, 'w') as pathf, open(textfile, 'w') as textf:
    for line in sys.stdin:
        wavpath, text = line.strip().split(maxsplit=1)

        _,_,wavfile = wavpath.split('/')
        m = re.match(r'(.*)_(.*)_(.*).wav', wavfile)
        
        spkrid = m.group(1).replace('-', '_')
        others = m.group(2) + '_' + m.group(3)
        
        key = spkrid + '-' + others

        print(f'{key}\t{text}', file=textf)
        print(f'{key}\tver1.0/01_jpn/{wavpath}', file=pathf)
        

    
