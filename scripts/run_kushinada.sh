#!/bin/bash

##
if [ $# -le 6 ]; then
    echo "usage: corpus device model nbeam lmw ctcw penalty [set]"
    exit;
fi

#
corpus=$1
device=$2

modelname="$3"
nbeam=$4
lmw=$5
ctcw=$6
penalty=$7

#
topdir=../

# 
if [ $# -le 7 ]; then
    resultpath=espnet/"${modelname}"/nbeam-${nbeam}_ctcw-${ctcw}_lmw-${lmw}_penalty-${penalty}/
    mkdir -p "${resultpath}"

    listfile=list/${corpus}_key-path.txt
    resultfile="${resultpath}"/result_key-text.txt
    
    # recognition
    if [ ! -s "${resultfile}" ]; then
	. ${topdir}/venv/kushinada/bin/activate
	python3 ${topdir}/pysctkja/espnet_batch.py "${modelname}" ${listfile} "${resultfile}" \
                    --beam_size ${nbeam} --ctc_weight ${ctcw} --lm_weight ${lmw} --penalty ${penalty} \
                    --device ${device}
	deactivate
    fi
    
    # score
    sh ${topdir}/scripts/scores.sh ${topdir} "${resultfile}" "${resultpath}" \
       list/${corpus}_key-rawtext.txt \
       rule/regex

else
    for listname in ${@:8}; do        
        resultpath=espnet/"${modelname}"/nbeam-${nbeam}_ctcw-${ctcw}_lmw-${lmw}_penalty-${penalty}/set-${listname}/
        mkdir -p "${resultpath}"
        
        listfile=list/${corpus}_${listname}_key-path.txt
        resultfile="${resultpath}"/result_key-text.txt
        
        ###### recognition
        if [ ! -s "${resultfile}" ]; then
            . ${topdir}/venv/kushinada/bin/activate
            python3 ${topdir}/pysctkja/espnet_batch.py "${modelname}" ${listfile} "${resultfile}" \
                    --beam_size ${nbeam} --ctc_weight ${ctcw} --lm_weight ${lmw} --penalty ${penalty} \
                    --device ${device}
            deactivate
        fi
        
        ## score
        sh ${topdir}/scripts/scores.sh ${topdir} "${resultfile}" "${resultpath}" \
           list/${corpus}_${listname}_key-rawtext.txt \
           rule/regex_${listname}
    done
fi
