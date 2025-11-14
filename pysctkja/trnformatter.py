import sys

class CharFormatter:
    def __init__(self):
        pass

    def __call__(self, text):
        return self.proc(text)

    def proc(self, text):
        text = list(''.join(text.split()))
        return ' '.join(text)

###
def main():
    totrans = CharFormatter()
    for line in sys.stdin:
        line = line.strip()
        try:
            key, text = line.split('\t', maxsplit=1)
        except:
            print(f'[ERROR]: {line}', file=sys.stderr)
            quit()
        text = totrans(text)
        print(f'{text}\t({key})', flush=True)

if __name__ == '__main__':
    main()
    