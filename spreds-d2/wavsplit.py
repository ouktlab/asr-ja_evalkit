import sys
import subprocess

#wavpath = 'ver1.1/01_jpn/individual/segmented/WAVE/'
wavpath = sys.argv[1]

for line in sys.stdin:
    labfile = line.strip()
    wavhead = wavpath + labfile.replace('.lab', '')
    wavfile = wavhead + '.wav'

    count = 1
    splitfiles = []
    with open('aux/' + labfile) as f:
        for l in f:
            beg, end, lab = l.strip().split()

            if lab == 'sp':
                continue
            
            beg = float(beg)
            end = float(end)

            outfile = f'{wavhead}_S{count:01d}.wav'

            cmdstring = f'sox {wavfile} {outfile} trim {beg} {end-beg}'
            print(cmdstring, file=sys.stderr)
            subprocess.call(cmdstring, shell=True)
            count += 1
            splitfiles.append(outfile)

    print(f'{wavfile}\t{",".join(splitfiles)}')
