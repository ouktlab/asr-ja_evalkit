import sys

splitlist = sys.argv[1]

pathmap = {}
with open(splitlist) as f:
    for line in f:
        key, path = line.strip().split(maxsplit=1)
        pathmap[key] = path


for line in sys.stdin:
    line = line.strip()

    key, path = line.split(maxsplit=1)

    if (splitpath := pathmap.get(path)) is not None:
        print(f'{key}\t{pathmap[path]}')
    else:
        print(f'{key}\t{path}')
    
    
