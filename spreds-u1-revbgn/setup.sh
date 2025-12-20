####
stage=0
. ../venv/espnet/bin/activate

####
# download corpus
if [ $stage -le 0 ]; then
  wget https://ast-astrec.nict.go.jp/release/SPREDS-U1/ver1.0/SPREDS-U1.ver1.0.tar.xz
  tar Jxfv SPREDS-U1.ver1.0.tar.xz
  rm SPREDS-U1.ver1.0.tar.xz
fi

if [ $stage -le 1 ]; then
    wget https://openslr.trmal.net/resources/28/rirs_noises.zip
    unzip rirs_noises.zip
    rm rirs_noises.zip
fi

if [ $stage -le 2 ]; then
    git clone https://github.com/karolpiczak/ESC-50.git
fi

if [ $stage -le 3 ]; then
    ln -s ../spreds-u1/label2pair.py ./
fi

# gen base key-path and key-text list
if [ $stage -le 4 ]; then
  mkdir -p list/
  cat ver1.0/01_jpn/LABEL/SPREDS-U1.ver1.0.label \
      | python3 label2pair.py list/base_key-path.txt list/base_key-rawtext.txt

  find ESC-50/ -name "*.wav" \
      | awk '{if (NR%2==0){print $1}}' \
       > list/base_noisepath.txt
fi

# gen reverberant and noisy data
if [ $stage -le 5 ]; then
    mkdir -p rule
    impbase=RIRS_NOISES/real_rirs_isotropic_noises/
    for reverb in near far; do
	impfile=${impbase}/RVB2014_type1_rir_largeroom1_${reverb}_angla.wav
	for snr in 10 30 50; do	
	    outbase=audio/snr-${snr}_reverb-${reverb}
	    
	    python3 synthesize.py \
	   	    list/base_key-path.txt \
		    list/base_noisepath.txt \
		    ${impfile} \
		    ${snr} \
		    ${outbase}
	    
	    cat list/base_key-path.txt \
		| sed -e 's|ver1.0/01_jpn/WAVE|'"${outbase}"'|' \
		      > list/spreds-u1-revbgn_snr-${snr}-reverb-${reverb}_key-path.txt
	    cp list/base_key-rawtext.txt list/spreds-u1-revbgn_snr-${snr}-reverb-${reverb}_key-rawtext.txt
	    
	    ln -s ../../spreds-u1/rule/regex_lv-none.txt rule/regex_snr-${snr}-reverb-${reverb}_lv-none.txt
	    ln -s ../../spreds-u1/rule/regex_lv-lax.txt rule/regex_snr-${snr}-reverb-${reverb}_lv-lax.txt
	done
    done
fi

deactivate
