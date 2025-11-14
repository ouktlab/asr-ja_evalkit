####
stage=0

####
# download corpus

if [ $stage -le 0 ]; then
  wget https://ast-astrec.nict.go.jp/release/SPREDS-D2/ver1.1/SPREDS-D2.ver1.1.tar.xz
  tar Jxfv SPREDS-D2.ver1.1.tar.xz
  rm SPREDS-D2.ver1.1.tar.xz
fi

# gen key-path list
if [ $stage -le 1 ]; then
  mkdir -p list/  
  find ver1.1/01_jpn/ -name "*.wav" | grep "/segmented/" | grep -v "_S" \
      | sort \
      | sed -e 's|.*/\(.*\)-\(.*\)-\(.*\)-\(.*\)_\(.*\)_\(.*\).wav|\1_\2_\3_\4-\5_\6 \0|' \
	    > list/spreds-d2_key-path.txt
fi

#
if [ $stage -le 2 ]; then
  mkdir -p list/  

  find ver1.1/01_jpn/ -name "*.label" | grep "/segmented/" \
      | awk '{print "cat " $1}' \
      | sh \
      | sed -e 's|\(.*\)-\(.*\)-\(.*\)-\(.*\)_\(.*\)_\(.*\).wav\t\(.*\)|\1_\2_\3_\4-\5_\6\t\7|' \
      | sort \
      | python3 removetag.py \
		> list/spreds-d2_key-rawtext.txt
fi

# split
if [ $stage -le 3 ]; then
    cat aux/segmentlist.txt \
	| python3 wavsplit.py ver1.1/01_jpn/individual/segmented/WAVE/ \
		  > aux/split_wav-split.txt
fi

# replace
if [ $stage -le 4 ]; then
    mv list/spreds-d2_key-path.txt list/spreds-d2_key-path.txt.org
    cat list/spreds-d2_key-path.txt.org \
	| python3 embedpath.py aux/split_wav-split.txt \
		  > list/spreds-d2_key-path.txt
fi
