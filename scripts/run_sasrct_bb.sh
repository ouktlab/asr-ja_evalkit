#!/bin/bash

##
if [ $# -le 9 ]; then
    echo "usage: corpus device sasrmodel tokenizer sctmodel sasr_nbeam lmw ctcw penalty sct_nbeam [set]"
    exit;
fi

#
corpus=$1
device=$2

sasr_model=$3
tokenizer=$4
sct_model=$5
sasr_nbeam=$6
lmw=$7
ctcw=$8
penalty=$9
sct_nbeam=${10}

#
topdir=../

# 
if [ $# -le 10 ]; then
    resultpath=sasrct_bb/${sasr_model}/nbeam-${sasr_nbeam}_ctcw-${ctcw}_lmw-${lmw}_penalty-${penalty}/${sct_model}/nbeam-${sct_nbeam}
    mkdir -p ${resultpath}

    listfile=list/${corpus}_key-path.txt
    resultfile=${resultpath}/result_key-text.txt
    sasrfile=${resultpath}/sasr_result_key-text.txt
    
    # recognition
    if [ ! -s ${resultfile} ]; then
	. ${topdir}/venv/espnet/bin/activate	
	python3 ${topdir}/pysctkja/sasrct_bb_batch.py ${sasr_model} ${tokenizer} ${sct_model} ${listfile} ${resultfile} ${sasrfile} \
                    --sasr_beam_size ${sasr_nbeam} --ctc_weight ${ctcw} --lm_weight ${lmw} --penalty ${penalty} \
                    --sct_beam_size ${sct_nbeam} --device ${device} --nbest ${sasr_nbeam}
	deactivate
    fi
    
    # score
    sh ${topdir}/scripts/scores.sh ${topdir} ${resultfile} ${resultpath} \
       list/${corpus}_key-rawtext.txt \
       rule/regex

else
    for listname in ${@:11}; do        
        resultpath=sasrct_bb/${sasr_model}/nbeam-${sasr_nbeam}_ctcw-${ctcw}_lmw-${lmw}_penalty-${penalty}/${sct_model}/nbeam-${sct_nbeam}/set-${listname}/
        mkdir -p ${resultpath}
        
        listfile=list/${corpus}_${listname}_key-path.txt
        resultfile=${resultpath}/result_key-text.txt
        sasrfile=${resultpath}/sasr_result_key-text.txt
	
        ###### recognition
        if [ ! -s ${resultfile} ]; then
            . ${topdir}/venv/espnet/bin/activate
            python3 ${topdir}/pysctkja/sasrct_bb_batch.py ${sasr_model} ${tokenizer} ${sct_model} ${listfile} ${resultfile} ${sasrfile} \
                    --sasr_beam_size ${sasr_nbeam} --ctc_weight ${ctcw} --lm_weight ${lmw} --penalty ${penalty} \
                    --sct_beam_size ${sct_nbeam} --device ${device} --nbest ${sasr_nbeam}
            deactivate
        fi
        
        ## score
        sh ${topdir}/scripts/scores.sh ${topdir} ${resultfile} ${resultpath} \
           list/${corpus}_${listname}_key-rawtext.txt \
           rule/regex_${listname}
    done
fi
