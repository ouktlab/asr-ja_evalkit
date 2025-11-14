####
stage=0

####
# download corpus

if [ $stage -le 0 ]; then
  wget https://ast-astrec.nict.go.jp/release/SPREDS-D1/ver1.3/SPREDS-D1.ver1.3.ja.tar.xz
  tar Jxfv SPREDS-D1.ver1.3.ja.tar.xz
  rm SPREDS-D1.ver1.3.ja.tar.xz
fi

# gen key-path list
if [ $stage -le 1 ]; then
  mkdir -p list/  
  for dataset in A-0001 A-0002 A-0003 B-0001 B-0002; do
    find ver1.3/ -name "*.wav" | grep "/segmented/" | grep ${dataset} \
      | sort \
      | sed -e 's|.*/\(.*\)-\(.*\)-\(.*\)-\(.*\)_\(.*\)_\(.*\).wav|\1_\2_\3_\4-\5_\6 \0|' \
	    > list/spreds-d1_${dataset}_key-path.txt
  done  
fi

#
if [ $stage -le 2 ]; then
  mkdir -p list/  
  for dataset in A-0001 A-0002 A-0003 B-0001 B-0002; do
    find ver1.3/ -name "*.label" | grep "/segmented/" | grep ${dataset} \
      | awk '{print "cat " $1}' \
      | sh \
      | sed -e 's|\(.*\)-\(.*\)-\(.*\)-\(.*\)_\(.*\)_\(.*\).wav\t\(.*\)|\1_\2_\3_\4-\5_\6\t\7|' \
      | sort \
      | python3 removetag.py \
		> list/spreds-d1_${dataset}_key-rawtext.txt
  done  
fi
