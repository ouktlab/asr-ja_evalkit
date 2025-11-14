#
if [ $# -ne 5 ]; then
    echo "usage: topdir resultfile resultpath refkeytext dictfileheader"
    exit;
fi

#
topdir=$1
resultfile="${2}"
resultpath="${3}"
rawtext="${4}"
dictfileheader=$5

#
tagger_venv=fugashi
charnorm=charnorm-v1
tagger=fugashi-v1

#
scriptdir=${topdir}/scripts/

###
. ${topdir}/venv/${tagger_venv}/bin/activate

####### raw score ######
# ref
reffile="${resultpath}"/ref_rawtext.txt
hypfile="${resultpath}"/hyp_rawtext.txt
scorefile="${resultpath}"/score_${charnorm}_rawtext.txt

python3 ${topdir}/pyscliteja.py "${rawtext}" "${resultfile}" \
	"${reffile}" "${hypfile}" --scorefile "${scorefile}" \
	--charnorm ${charnorm} \
	--disable_adjust

####### word-normalization ######
for level in none lax; do
    # ref
    refsetfile="${resultpath}"/ref_lemmaset_${charnorm}_${tagger}_lv-${level}.txt
    reffile="${resultpath}"/ref_${charnorm}_${tagger}_rule-${level}.txt
    
    # hyp
    hypfile="${resultpath}"/hyp_${charnorm}_${tagger}_rule-${level}.txt

    # rulefile
    rulefile=${dictfileheader}_lv-${level}.txt
    
    #
    scorefile="${resultpath}"/score_${charnorm}_${tagger}_rule-${level}.txt

    python3 ${topdir}/pyscliteja.py "${rawtext}" "${resultfile}" \
	"${reffile}" "${hypfile}" --scorefile "${scorefile}" \
	--charnorm ${charnorm} \
	--pre_rulefile ${rulefile} \
	--tagger ${tagger} \
	--ref_lemma "${refsetfile}"
done

deactivate

