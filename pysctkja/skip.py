import sys

for line in sys.stdin:
    line = line.replace('***', '**')
    print(line)
