import sys

transcript = {}

transfile = sys.argv[1]

with open(transfile) as f:    
    for line in f:
        line = line.strip()
        tag, _, rawtext = line.split('|')
        transcript[tag] = rawtext

for line in sys.stdin:
    line = line.strip()
    
    key, path = line.split(maxsplit=1)
    spkr, tag = key.split('_', maxsplit=1)
    rawtext = transcript[tag]

    print(f'{key}\t{rawtext}')
