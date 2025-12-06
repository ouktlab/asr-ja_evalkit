####
stage=0

####
# download corpus
if [ $stage -le 0 ]; then
  # please download audio data by manual  
  unzip cpjd_ver1.zip
  rm cpjd_ver1.zip
fi

# gen key-path list
if [ $stage -le 1 ]; then
  mkdir -p list/  
  find cpjd_ver1/ -name "*.wav" \
      | grep -v clean | sort \
      | sed -e 's|.*/\(....\)_.*/\(.*\).wav|\1-\2\t\0|' \
	    > list/cpjd_key-path.txt
fi

# gen key-rawtext list
if [ $stage -le 2 ]; then
  rm list/cpjd_key-rawtext.txt
  touch list/cpjd_key-rawtext.txt
  for transfile in `find cpjd_ver1/ -name "*trans*" | sort`; do
      spkrid=`echo ${transfile} | sed -e 's|.*/\(....\)_.*|\1|'`
      cat ${transfile} \
	  | awk '{if (length($0) > 0) {print $0}}' \
	  | sed -e 's|^\(...\): |'${spkrid}'-\1\t|' \
	  | sed -e 's|^\(...\):|'${spkrid}'-\1\t|' \
	  | sed -e 's|^\(.\): |F007-00\1\t|' \
	  | sed -e 's|^\(..\): |F007-0\1\t|' \
	  | sed -e 's|（または、えいかもね）||' \
	  | sed -e 's|．$||' \
	  | sed -e 's|\.$||' \
	  | grep -v "F007-0.." \
	  | python3 filter.py list/cpjd_key-path.txt \
		>> list/cpjd_key-rawtext.txt
  done
fi
