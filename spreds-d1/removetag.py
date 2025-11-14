import sys
import re

pat_rm = re.compile(r'\[<(nos|unk|lgh)>\]')
pat_tag = re.compile(r'\[\<(ack|fil|unk|nam)\>/(.+?)\]')
pat_wrd = re.compile(r'\[(.+?)/(.+?)\]')

for line in sys.stdin:
    key, text = line.strip().split(maxsplit=1)

    text_wotag = text.replace('>fil>', '<fil>')
    text_wotag = text_wotag.replace('<ack/', '<ack>/')
    text_wotag = text_wotag.replace('<nam/', '<nam>/')
    text_wotag = pat_rm.sub(r'', text_wotag)
    text_wotag = pat_tag.sub(r'\2', text_wotag)
    text_wotag = pat_wrd.sub(r'\1', text_wotag)

    if len(text_wotag) == 0:
        text_wotag = '*'

    print(f'{key}\t{text_wotag}')
