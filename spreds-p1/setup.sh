####
stage=0

####
# download corpus

if [ $stage -le 0 ]; then
  wget https://ast-astrec.nict.go.jp/release/SPREDS-P1/ver1.0/SPREDS-P1.ver1.0.tar.xz
  tar Jxfv SPREDS-P1.ver1.0.tar.xz
  rm SPREDS-P1.ver1.0.tar.xz
fi

# gen key-path and key-text list
if [ $stage -le 1 ]; then
  mkdir -p list/
  cat ver1.0/01_jpn/segmented/LABEL/* \
    | python3 label2pair.py list/spreds-p1_key-path.txt list/spreds-p1_key-rawtext.txt
fi
