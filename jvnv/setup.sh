####
stage=0

####
# download corpus
if [ $stage -le 0 ]; then
  wget https://ss-takashi.sakura.ne.jp/corpus/jvnv/jvnv_ver1.zip
  unzip jvnv_ver1.zip
  rm jvnv_ver1.zip
fi

# downsampling to 16kHz
if [ $stage -le 1 ]; then
  rm -f __exe.sh; touch __exe.sh
  for wavfile in `find jvnv_v1/ -name "*.wav"`; do
    flacfile=`echo ${wavfile} | sed -e 's|jvnv_v1|data|' | sed -e 's|.wav|.flac|'`
    dirname=`dirname ${flacfile}`

    if [ ! -d ${dirname} ]; then
      mkdir -p ${dirname}
    fi

    echo "ffmpeg -i ${wavfile} -vn -ar 16000 -ac 1 -acodec flac -f flac ${flacfile}" >> __exe.sh
  done
  cat __exe.sh | xargs -P 4 -i sh -c '{}'
fi

# gen key-path list
if [ $stage -le 2 ]; then
  mkdir -p list/  
  for dataset in anger disgust fear happy sad surprise; do
      find data/ -name "*.flac" \
	  | grep ${dataset} \
	  | sort \
	  | sed -e 's|.*/\(.*\).flac|\1 \0|' \
		> list/jvnv_${dataset}_key-path.txt
  done
fi

# gen key-rawtext list
if [ $stage -le 3 ]; then
  for dataset in anger disgust fear happy sad surprise; do
    cat list/jvnv_${dataset}_key-path.txt \
	| python3 trans2text.py jvnv_v1/transcription.csv \
	     > list/jvnv_${dataset}_key-rawtext.txt
   done
fi
