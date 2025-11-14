#!/bin/bash

##
if [ $# -le 1 ]; then
    echo "usage: corpus device [set]"
    exit;
fi

#
corpus=$1
device=$2

#
topdir=../

# 
if [ $# -le 2 ]; then
    resultpath=whisper/large-v3/
    mkdir -p ${resultpath}
        
    listfile=list/${corpus}_key-path.txt
    resultfile=${resultpath}/result_key-text.txt
    
    # recognition
    if [ ! -s ${resultfile} ]; then
	. ${topdir}/venv/whisper/bin/activate       
	python3 ${topdir}/pysctkja/whisperv3.py ${listfile} ${resultfile} --device ${device}
	deactivate
    fi
    
    # score
    sh ${topdir}/scripts/scores.sh ${topdir} ${resultfile} ${resultpath} \
       list/${corpus}_key-rawtext.txt \
       rule/regex

else
    for listname in ${@:3}; do        
        resultpath=whisper/large-v3/set-${listname}/
        mkdir -p ${resultpath}
        
        listfile=list/${corpus}_${listname}_key-path.txt
        resultfile=${resultpath}/result_key-text.txt
        
        ###### recognition
        if [ ! -s ${resultfile} ]; then
	    . ${topdir}/venv/whisper/bin/activate       
	    python3 ${topdir}/pysctkja/whisperv3.py ${listfile} ${resultfile} --device ${device}
	    deactivate
        fi
        
        ## score
        sh ${topdir}/scripts/scores.sh ${topdir} ${resultfile} ${resultpath} \
           list/${corpus}_${listname}_key-rawtext.txt \
           rule/regex_${listname}
    done
fi

