import sys
import os
import numpy as np
import librosa
import soundfile as sf

def bwd_padding(data, nlen):
    n = int(np.ceil(np.log2(nlen)))
    return np.concatenate([data, np.zeros((2**n-len(data)))])

def fft_conv(s, w):
    length = len(w) + len(s) - 1
    w_ = bwd_padding(w, length)
    s_ = bwd_padding(s, length)

    W = np.fft.rfft(w_)
    S = np.fft.rfft(s_)
    y = np.fft.irfft(W * S, len(s_)).real[:length]

    return y

def main(srclist, noiselist, impfile, snr, outbase):    
    imp, sr_imp = librosa.load(impfile, sr=16000, mono=False)
    imp = imp[0,:]    # use 1st channel. no reason.
    impoffset = 2400  #
    
    len_fade = int(0.05 * sr_imp) # linear fade-in/out for noise wav
    w_fade = np.linspace(0.0, 1.0, len_fade)    

    with open(srclist) as f_src, open(noiselist) as f_noise:
        for line_src, line_noise in zip(f_src, f_noise):
            key, speechfile = line_src.strip().split()
            noisefile = line_noise.strip()

            print(f'[LOG]: now process {speechfile}, {noisefile}', flush=True)
            
            wav_s, sr_s = librosa.load(speechfile, sr=16000, mono=False)
            wav_n, sr_n = librosa.load(noisefile, sr=16000, mono=False)
            wav_x = fft_conv(wav_s, imp)[impoffset:impoffset+len(wav_s)]

            wav_n[:len_fade] *= w_fade
            wav_n[-len_fade:] *= (1.0 - w_fade)

            len_x = len(wav_x)
            len_n = len(wav_n)

            if len_x > len_n:
                offset = int((len_x - len_n)/2) - 1
                P_x = np.mean(wav_x[offset:offset+len_n]**2)
                P_n = np.mean(wav_n**2)
                a = np.sqrt(P_x/P_n) * np.power(10, -snr/20)
                wav_x[offset:offset+len_n] += wav_n * a
            else:
                P_x = np.mean(wav_x**2)
                P_n = np.mean(wav_n[:len_x]**2)
                a = np.sqrt(P_x/P_n) * np.power(10, -snr/20)
                wav_x += wav_n[:len_x] * a

            max_s_v = np.max(np.abs(wav_s))
            max_x_v = np.max(np.abs(wav_x))

            wav_x = wav_x / max_x_v * max_s_v
            
            outfile = f'{outbase}/{speechfile}'.replace('ver1.0/01_jpn/WAVE/', '')

            dirname = os.path.dirname(outfile)
            os.makedirs(dirname, exist_ok=True)
            
            sf.write(outfile, wav_x, sr_s, format='WAV', subtype='PCM_16')

def usage():
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument('srclist', type=str)
    parser.add_argument('noiselist', type=str)
    parser.add_argument('impfile', type=str)
    parser.add_argument('snr', type=int)
    parser.add_argument('outbase', type=str)
    args = parser.parse_args()
    return args
    
if __name__ == '__main__':
    args = usage()
    main(args.srclist, args.noiselist, args.impfile,
         args.snr, args.outbase)
    
