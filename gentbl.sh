mkdir -p result
find . -name "score_charnorm-v1_rawtext.txt" \
    | grep -v sample \
    | python3 pysctkja/summarize.py cui \
	      > result/detailed_score_charnorm-v1_rawtext.txt
find . -name "score_charnorm-v1_fugashi-v1_rule-none.txt" \
    | grep -v sample \
    | python3 pysctkja/summarize.py cui \
	      > result/detailed_score_charnorm-v1_fugashi-v1_rule-none.txt
find . -name "score_charnorm-v1_fugashi-v1_rule-lax.txt" \
    | grep -v sample \
    | python3 pysctkja/summarize.py cui \
	      > result/detailed_score_charnorm-v1_fugashi-v1_rule-lax.txt


find . -name "score_charnorm-v1_rawtext.txt" \
    | grep -v sample \
    | python3 pysctkja/summarize.py sumcer \
	      --tagfile scripts/sumcer_tag.txt \
	      > result/summary_score_charnorm-v1_rawtext.txt
find . -name "score_charnorm-v1_fugashi-v1_rule-none.txt" \
    | grep -v sample \
    | python3 pysctkja/summarize.py sumcer \
	      --tagfile scripts/sumcer_tag.txt \
	      > result/summary_score_charnorm-v1_fugashi-v1_rule-none.txt
find . -name "score_charnorm-v1_fugashi-v1_rule-lax.txt" \
    | grep -v sample \
    | python3 pysctkja/summarize.py sumcer \
	      --tagfile scripts/sumcer_tag.txt \
	      > result/summary_score_charnorm-v1_fugashi-v1_rule-lax.txt

