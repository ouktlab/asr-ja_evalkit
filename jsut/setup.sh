####
stage=0

####
# download corpus
if [ $stage -le 0 ]; then
  wget http://ss-takashi.sakura.ne.jp/corpus/jsut_ver1.1.zip
  unzip jsut_ver1.1.zip
  rm jsut_ver1.1.zip
fi

# downsampling to 16kHz
if [ $stage -le 1 ]; then
  rm -f __exe.sh; touch __exe.sh
  for wavfile in `find jsut_ver1.1/ -name "*.wav"`; do
    flacfile=`echo ${wavfile} | sed -e 's|jsut_ver1.1|data|' | sed -e 's|/wav/|/flac16k/|' | sed -e 's|.wav|.flac|'`
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
  for dataset in basic5000 countersuffix26 loanword128 \
			   onomatopee300 precedent130 repeat500 \
			   travel1000 utparaphrase512 voiceactress100; do
    find data/${dataset} -name "*.flac" \
      | sort \
      | sed -e 's|.*/\(.*\).flac|\1 \0|' \
	    > list/jsut_${dataset}_key-path.txt
  done  
fi

# gen key-rawtext list
if [ $stage -le 3 ]; then
   for dataset in basic5000 countersuffix26 loanword128 \
			   onomatopee300 precedent130 repeat500 \
			   travel1000 utparaphrase512 voiceactress100; do
     cat jsut_ver1.1/${dataset}/transcript_utf8.txt \
       | awk -F':' '{print $1 " " $2}' \
	     > list/jsut_${dataset}_key-rawtext.txt
   done
fi
