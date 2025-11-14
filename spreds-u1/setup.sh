####
stage=0

####
# download corpus

if [ $stage -le 0 ]; then
  wget https://ast-astrec.nict.go.jp/release/SPREDS-U1/ver1.0/SPREDS-U1.ver1.0.tar.xz
  tar Jxfv SPREDS-U1.ver1.0.tar.xz
  rm SPREDS-U1.ver1.0.tar.xz
fi

# gen key-path and key-text list
if [ $stage -le 1 ]; then
  mkdir -p list/
  cat ver1.0/01_jpn/LABEL/SPREDS-U1.ver1.0.label \
    | python3 label2pair.py list/spreds-u1_key-path.txt list/spreds-u1_key-rawtext.txt
fi
