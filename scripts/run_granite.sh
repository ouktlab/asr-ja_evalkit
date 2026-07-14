#!/bin/bash

##
if [ $# -le 1 ]; then
    echo "usage: corpus device modelpath [set]"
    exit;
fi

#
corpus=$1
device=$2
modelpath=$3

#
topdir=../

# 
if [ $# -le 3 ]; then
    resultpath=granite/${modelpath}
    mkdir -p ${resultpath}

    listfile=list/${corpus}_key-path.txt
    resultfile=${resultpath}/result_key-text.txt
    
    # recognition
    if [ ! -s ${resultfile} ]; then
	. ${topdir}/venv/granite/bin/activate
	python3 ${topdir}/pysctkja/granite_batch.py ${modelpath} ${listfile} ${resultfile} --device ${device}
	deactivate
    fi
    
    # score
    sh ${topdir}/scripts/scores.sh ${topdir} ${resultfile} ${resultpath} \
       list/${corpus}_key-rawtext.txt \
       rule/regex

else
    for listname in ${@:4}; do        
        resultpath=granite/${modelpath}/set-${listname}/
        mkdir -p ${resultpath}
        
        listfile=list/${corpus}_${listname}_key-path.txt
        resultfile=${resultpath}/result_key-text.txt
        
        ###### recognition
        if [ ! -s ${resultfile} ]; then
            . ${topdir}/venv/granite/bin/activate
            python3 ${topdir}/pysctkja/granite_batch.py ${modelpath} ${listfile} ${resultfile} --device ${device}
            deactivate
        fi
        
        ## score
        sh ${topdir}/scripts/scores.sh ${topdir} ${resultfile} ${resultpath} \
           list/${corpus}_${listname}_key-rawtext.txt \
           rule/regex_${listname}
    done
fi
