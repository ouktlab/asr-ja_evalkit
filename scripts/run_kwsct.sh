#!/bin/bash

##
if [ $# -le 4 ]; then
    echo "usage: corpus device sasrmodel tokenizer sctmodel [set]"
    exit;
fi

#
corpus=$1
device=$2

sasr_model=$3
tokenizer=$4
sct_model=$5

#
topdir=../

# 
if [ $# -le 5 ]; then
    resultpath=kwsct/${sasr_model}/${sct_model}/
    mkdir -p ${resultpath}

    listfile=list/${corpus}_key-path.txt
    resultfile=${resultpath}/result_key-text.txt
    sasrfile=${resultpath}/sasr_result_key-text.txt
    
    # recognition
    if [ ! -s ${resultfile} ]; then
	. ${topdir}/venv/espnet/bin/activate	
	python3 ${topdir}/pysctkja/kwsct_batch.py ${sasr_model} ${tokenizer} ${sct_model} ${listfile} ${resultfile} ${sasrfile} \
                --device ${device}
	deactivate
    fi
    
    # score
    sh ${topdir}/scripts/scores.sh ${topdir} ${resultfile} ${resultpath} \
       list/${corpus}_key-rawtext.txt \
       rule/regex

else
    for listname in ${@:6}; do        
        resultpath=kwsct/${sasr_model}/${sct_model}/set-${listname}/
        mkdir -p ${resultpath}
        
        listfile=list/${corpus}_${listname}_key-path.txt
        resultfile=${resultpath}/result_key-text.txt
        sasrfile=${resultpath}/sasr_result_key-text.txt
	
        ###### recognition
        if [ ! -s ${resultfile} ]; then
            . ${topdir}/venv/espnet/bin/activate
            python3 ${topdir}/pysctkja/kwsct_batch.py ${sasr_model} ${tokenizer} ${sct_model} ${listfile} ${resultfile} ${sasrfile} \
                    --device ${device}
            deactivate
        fi
        
        ## score
        sh ${topdir}/scripts/scores.sh ${topdir} ${resultfile} ${resultpath} \
           list/${corpus}_${listname}_key-rawtext.txt \
           rule/regex_${listname}
    done
fi
