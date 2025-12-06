import sys

pathfile = sys.argv[1]

entry = set()
with open(pathfile) as f:
    for x in f:
        key, path = x.strip().split(maxsplit=1)
        entry.add(key)

for line in sys.stdin:
    line = line.strip()
    key, text = line.split(maxsplit=1)
    if key in entry:
        print(line)
        
