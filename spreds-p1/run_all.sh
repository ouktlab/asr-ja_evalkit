#
device=cuda:1
corpus=spreds-p1

#
espnet_csjcore=true #false
espnet_csjfull=true #false
espnet_corpus10=true #false

espnet_stream_corpus10=true

#
sasrct_corpus10=true #false

#
funasr=true #false
espnet_laborotv=true #false
whisperv3=true #false
reazon=true #false
nue=true #false

#
espnet_csjfullcon=true #false

#
kotobaw=true

# 
kushinada=true


#########
if "${espnet_csjcore}"; then
    modelname=ouktlab/espnet_csjcore_asr_train_asr_transformer_lm_rnn
    bash ../scripts/run_espnet.sh ${corpus} ${device} ${modelname} 20 0.30 0.21 0.0
fi

if "${espnet_csjfull}"; then
    modelname=ouktlab/espnet_csj_asr_train_asr_transformer_lm_rnn
    bash ../scripts/run_espnet.sh ${corpus} ${device} ${modelname} 20 0.30 0.21 0.0
fi

if "${espnet_corpus10}"; then
    modelname=ouktlab/espnet_asr-ja-mc_am-transformer-robustcorpus10_lm-transformer-corpus10-bccwj-wiki40b
    bash ../scripts/run_espnet.sh ${corpus} ${device} ${modelname} 20 0.35 0.195 0.0
fi

if "${espnet_stream_corpus10}"; then
    modelname=ouktlab/espnet_asr-ja-mc-stream_am-transformer-robustcorpus10_lm-transformer-corpus10-bccwj-wiki40b
    bash ../scripts/run_espnet_stream.sh ${corpus} ${device} ${modelname} 20 0.35 0.195 0.0
fi

##########
if "${sasrct_corpus10}"; then
    sasr_model=ouktlab/espnet_asr-ja-kc_am-transformer-robustcorpus10_lm-transformer-corpus10-bccwj-wiki40b
    tokenizer=ouktlab/character_tokenizer_jis_v2
    sct_model=ouktlab/t5_sct-jis-v2_corpus10-bccwj-wiki40b_mask-1.00
    bash ../scripts/run_sasrct.sh ${corpus} ${device} ${sasr_model} ${tokenizer} ${sct_model} 20 0.35 0.195 0.0 15
fi

##########
if "${espnet_laborotv}"; then
    modelname="Shinji Watanabe/laborotv_asr_train_asr_conformer2_latest33_raw_char_sp_valid.acc.ave"
    bash ../scripts/run_espnet.sh ${corpus} ${device} "${modelname}" 20 0.30 0.21 0.0
fi

##########
if "${funasr}"; then
    bash ../scripts/run_funasr.sh ${corpus} ${device}
fi

##########
if "${reazon}"; then
    bash ../scripts/run_reazon.sh ${corpus} ${device}
fi

##########
if "${whisperv3}"; then
    bash ../scripts/run_whisperv3.sh ${corpus} ${device}
fi

##########
if "${nue}"; then
    bash ../scripts/run_nue.sh ${corpus} ${device}
fi

##########
if "${espnet_csjfullcon}"; then
    modelname=ouktlab/espnet_csj_asr_train_asr_conformer_lm_rnn
    bash ../scripts/run_espnet.sh ${corpus} ${device} ${modelname} 20 0.30 0.21 0.0
fi

##########
if "${kotobaw}"; then
    bash ../scripts/run_kotobaw.sh ${corpus} ${device}
fi

##########
if "${kushinada}"; then
    modelname=imprt/kushinada-hubert-large-laborotv2-asr
    bash ../scripts/run_kushinada.sh ${corpus} ${device} ${modelname} 20 0.30 0.21 0.0
fi
