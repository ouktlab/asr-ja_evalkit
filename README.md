# ASR-ja Evaluation Kit
This repository provides a sample toolkit for evaluation of **Japanese** automatic speech recognition (ASR). 
The focus of this evaluation kit is orthographic variants (表記ゆれ). 
The performance of ASR models may be measured more accurately by using this toolkit. 

These examples and scripts can be used for academic research and education. 
Please use carefully because some bugs and errors may remain. 

## Features
- Support text normalization using solid dictionary [`UniDic`](https://clrd.ninjal.ac.jp/unidic/) (with [`Fugashi`](https://github.com/polm/fugashi) interface of [`MeCab`](https://taku910.github.io/mecab/)) for orthographic variants (表記ゆれ)
- Provide sample codes for CER evaluation of several datasets mainly available on Web

##  Requirements
OS: Ubuntu 22.04 or 24.04

Python: 3.10 or later

Python libraries
 - pyyaml
 - fugashi[unidic]


Other toolkit or software: we need to install them by `sudo apt install` command. 
 - sctk ([SCTK](https://github.com/usnistgov/SCTK))
 - ffmpeg (for reading audio file in ASR processing)

Required python libraries are different for each ASR model
 - espnet
 - torchaudio
 - torchcodec
 - transformers
 - soxr 
 - espnet_model_zoo
 - numpy
 - sentencepiece
 - nue-asr
 - Cython
 - openai-whisper
 - funasr


## Influence of Orthographic Variants and Its Reduction
### What happens
The reference text and ASR result text are usually suffered from orthographic variants (`表記ゆれ`, `different spelling`), which may *sometimes* prevent us from evaluating ASR performance correctly. 
- Japanese writing system: Hiragana, Katakana, Kanji, alphabet, symbol, numbers
- Reference (corpus/test set transcriptions)
  - strict rules and checks are required when human transcribes speech data set
  - such rules are also different among corpora
- Hypothesis (ASR result)
  - recent end-to-end models are trained on various corpora/text data set, resulting in inconsistent representations of words
  - word representations of ASR/LM output sometimes change according to the context

For example, CER of the following recognition results will be worse while the meaning of the sentence is almost the same. 
```
Ref: 足立さん身長百八十五センチメートルなんだ物凄くおっきいね
Hyp: 安達さん身長185cmなんだものすごく大きいね
```
Even our human cannot determine '足立' or '安達' from audio signal.    
Actual CER of the example above will be like
```
Scores: (#C #S #D #I) 11 10 7 2
REF:  足 立 さ ん 身 長 百 八 十 五 セ ン チ メ ー ト ル な ん だ ** ** 物 凄 く お っ き い ね 
HYP:  安 達 さ ん 身 長 ** ** ** ** ** ** 1  8  5  C  M  な ん だ も の す ご く ** 大 き い ね 
Eval: S  S             D  D  D  D  D  D  S  S  S  S  S          I  I  S  S     D  S 
```

Other examples of `表記ゆれ` are as follows:
- personal pronoun: ワタシ - わたし - 私
- name: 渡辺 - 渡部 (ワタナベ)
- number: 一万 - 1万 - 10000
- symbol, unit: % - パーセント, g - グラム
- proper noun, English word: Twitter - ツイッター, Tower - タワー
- okurigana: 行なった - 行った (おこなった)
- adverb: ようやく - 漸く
- onomatopoeia: きらきら - キラキラ

### Solution using solid dictionary and morphological analyzer
Orthographic variants of major words have been well maintained, and they are summarized as dictionary database. By analyzing Japanese sentence with such dictionary, we can resolve the orthographic variants between reference and hypothesis **to some extent (exceptions always exist)** by considering context. 

The following sentences are [`lemmna` and `surface`] of words after applying morphological analyzer (`fugashi` with `UniDic`).
```
Ref: [["アダチ", "足立"], ["さん", "さん"], ["身長", "身長"], ["百八十五", "185"], ["センチメートル", "センチメートル"], ["だ", "な"], ["の", "ん"], ["だ", "だ"], ["物凄い", "物凄く"], ["大きい", "おっきい"], ["ね", "ね"]]
Hyp: [["アダチ", "安達"], ["さん", "さん"], ["身長", "身長"], ["185", "185"], ["センチメートル", "cm"], ["だ", "な"], ["の", "ん"], ["だ", "だ"], ["物凄い", "ものすごく"], ["大きい", "大きい"], ["ね", "ね"]]
```
We can see that `lemma` entry can be hint for resolving orthographic variants. If we adjust the surface of hypothesis words to that of reference words, the character distance between ref. and hyp. will be reduced.  
```
Ref: 足立さん身長185センチメートルなんだ物凄くおっきいね
Hyp: 足立さん身長185センチメートルなんだ物凄くおっきいね
```
Here, numbers are also normalized by other processing.   
Actual CER of the example above will be like
```
Scores: (#C #S #D #I) 27 0 0 0
REF:  足 立 さ ん 身 長 1 8 5 セ ン チ メ ー ト ル な ん だ 物 凄 く お っ き い ね 
HYP:  足 立 さ ん 身 長 1 8 5 セ ン チ メ ー ト ル な ん だ 物 凄 く お っ き い ね 
Eval: 
```
Of course, the normalization policy above (e.g., handling of name) is not perfect and should be improved. However, ASR performance and its comparison in CER or WER will be more reliable than before by introducing this processing.  


Please also see other tag information in [UniDic manual](https://clrd.ninjal.ac.jp/unidic/UNIDIC_manual.pdf).

## Implementation
The actual procedure is listed below. 
1. Character normalization: `unicode.normalize` with `NFKC` option
1. String replacement using *Rules* for exceptions (e.g., OOV of `UniDic`)
1. Apply morphological analyzer (`Fugashi`: `Mecab` with `Unidic`)
   - Numbers are also normalized to the mixed representation of number-Kanji, e.g., 1万, with best effort
1. Align hypothesis *words* with reference *words* using `lemma` entry in POS tag by DP
1. Replace the matched words into the `surface` representations of words in the reference text
1. Reconstruct text of hypothesis and reference
1. Run evaluation tools, e.g., for CER
   - `sctk sclite` ([SCTK](https://github.com/usnistgov/SCTK)) is used for CER calculation in our toolkit


The *Rules* are constructed by manual/hands after performance evaluation (by checking alignment between reference and hypothesis text). This force adjustment to reference text may be applied to OOV (no-entry word) of the dictionary or (our)insufficient text processing implementation. For example, 
- English sentences
- OOV of dict: Netflix - ネットフリックス
- Some words: 易しい - やさしい, 
- Kanji numbers: 二十一二十二: 2, 11, 20, 2 or 21, 22, or 2, 10, 2, 12, etc... 
- Numbers: 121314 - 12, 13, 14 or 1, 2, 1, 3, 1, 4 or 12万1314 or 12-1314
- Missing patterns caused by insufficient implementations


## How to use evaluation tool (after cloning repository)
You can calculate CER by preparing reference and hypothesis list files. 
Here, we show its example using sample files. 

### Setup
Only `sctk`, `fugashi` and `unidic` are required to use `pyscliteja.py`.
The minimum installation is as follows:

```
sudo apt install sctk
python3 -m venv venv/fugashi
. venv/fugashi/bin/activate
python3 -m pip install 'fugashi[unidic]' pyyaml
python3 -m unidic download
```

You can use `setup_for_tool.sh` for automatic installation.
```
sh setup_for_tool.sh
```

### Prepare reference and hypothesis list files
Sample lists are in the `sample` directory.
```
asr-ja_evalkit$ ls sample
egs_hyplist.txt  egs_reflist.txt  numlist.txt
```


There are two key-value list file (delimiter is `TAB`) corresponding to reference and hypothesis. 
```
asr-ja_evalkit$ cat sample/egs_reflist.txt
spkr01-uttr01   足立さん身長百八十五センチメートルなんだ物凄くおっきいね
asr-ja_evalkit$ cat sample/egs_hyplist.txt
spkr01-uttr01   安達さん身長185cmなんだものすごく大きいね
```

### Run scripts to process list files
#### Activate venv for fugashi
```
. venv/fugashi/bin/activate
```

#### Evaluation with normalization
We can calculate CER from the two list files. `ref_trn.txt` and `hyp_trn.txt` are saved, and they are used as input files for `sctk sclite` commands. `--scorefile` option specifies the CER score filename as output.
```
python3 pyscliteja.py sample/egs_reflist.txt sample/egs_hyplist.txt sample/ref_trn.txt sample/hyp_trn.txt --scorefile sample/score_with_normalize.txt
[LOG]: Namespace(ref_list='sample/egs_reflist.txt', hyp_list='sample/egs_hyplist.txt', ref_trn='sample/ref_trn.txt', hyp_trn='sample/hyp_trn.txt', scorefile='sample/score_with_normalize.txt', charnorm='charnorm-v1', pre_rulefile=None, tagger='fugashi-v1', disable_adjust=False, trnfmt='char', post_rulefile=None, ref_pre=None, hyp_pre=None, ref_adj=None, hyp_adj=None, ref_lemma=None, hyp_lemma=None)
[LOG]: load "CharNormalizerV1()" in PreProcessor
[LOG]: load "FugashiLemmaTaggerV1()"
[LOG]: load "CharFormatter()" in PostProcessor
```

We can confirm aliments of each sentence pair and total CER.
```
tail -n 6 sample/score_with_normalize.txt | head -n 4
Scores: (#C #S #D #I) 27 0 0 0
REF:  足 立 さ ん 身 長 1 8 5 セ ン チ メ ー ト ル な ん だ 物 凄 く お っ き い ね 
HYP:  足 立 さ ん 身 長 1 8 5 セ ン チ メ ー ト ル な ん だ 物 凄 く お っ き い ね 
Eval:                                                                                 
```
```
grep -e "Sum/" -e "Corr" sample/score_with_normalize.txt | head -n 2
       | SPKR   | # Snt # Wrd | Corr    Sub    Del    Ins    Err  S.Err |
       | Sum/Avg|    1     27 |100.0    0.0    0.0    0.0    0.0    0.0 |
```

#### Evaluation without normalization
We can disable the normalization by using option `--disable_adjust`. 
```
python3 pyscliteja.py sample/egs_reflist.txt sample/egs_hyplist.txt sample/ref_trn.txt sample/hyp_trn.txt --scorefile sample/
score_with_normalize.txt --disable_adjust
[LOG]: Namespace(ref_list='sample/egs_reflist.txt', hyp_list='sample/egs_hyplist.txt', ref_trn='sample/ref_trn.txt', hyp_trn='sample/hyp_trn.txt', scorefile='sample/score_with_normalize.txt', charnorm='charnorm-v1', pre_rulefile=None, tagger='fugashi-v1', disable_adjust=True, trnfmt='char', post_rulefile=None, ref_pre=None, hyp_pre=None, ref_adj=None, hyp_adj=None, ref_lemma=None, hyp_lemma=None)
[LOG]: load "CharNormalizerV1()" in PreProcessor
[LOG]: load "CharFormatter()" in PostProcessor
```

We can also confirm aliments of each sentence pair and total CER.
```
tail -n 6 sample/score_without_normalize.txt | head -n 4
Scores: (#C #S #D #I) 11 10 7 2
REF:  足 立 さ ん 身 長 百 八 十 五 セ ン チ メ ー ト ル な ん だ *** *** 物 凄 く お っ き い ね 
HYP:  安 達 さ ん 身 長 *** *** *** *** *** *** 1   8   5   C   M   な ん だ も の す ご く *** 大 き い ね 
Eval: S   S                   D   D   D   D   D   D   S   S   S   S   S               I   I   S   S       D   S         
```
```
grep -e "Sum/" -e "Corr" sample/score_without_normalize.txt | head -n 2
       | SPKR   | # Snt # Wrd | Corr    Sub    Del    Ins    Err  S.Err |
       | Sum/Avg|    1     28 | 39.3   35.7   25.0    7.1   67.9  100.0 |
```

## How to use evaluation scripts for each corpus (after cloning repository)
### Setup sub-toolkit and venv for ASR models
Run `setup.sh` in the top directory "asr-ja_evalkit" to setup all models automatically.
```
sh setup.sh
```

If you want to select models for installation, please modify the options in the shell script. The following is a minimum setting. 
```
###
stage=0

###
espnet=false 
whisper=false
reazon=false
nue=false
funasr=false
fugashi=true
```

### Preparation of each corpus and speech recognition
Move into the corpus directory.
```
asr-ja_evalkit$ cd spreds-d1
```

Run the corpus `setup.sh` to download corpus and to generate lists of transcription and audio filepath.
```
asr-ja_evalkit/spreds-d1$ sh setup.sh
```

Run `run_all.sh` to start recognition by each ASR model and CER computation.
```
asr-ja_evalkit/spreds-d1$ sh run_all.sh
```

### Summary of results
Run `gentbl.sh` at the top directory.
```
asr-ja_evalkit$ sh gentbl.sh
```

Summary of CER scores will be saved under the `result` directory.



## How to use as package
### Pip install via github
#### 0. Install system libraries
We need to install `sctk` for Ubuntu environment.
```
sudo apt install sctk
```

#### 1. Activate virtual environment
```
python3 -m venv venv
. venv/bin/activate
```

#### 2. Install asr-ja_evalkit by pip from GitHub
```
python3 -m pip install git+https://github.com/ouktlab/asr-ja_evalkit.git
```

We also need to install `UniDic` for `fugashi`. 
```
python3 -m unidic download
```
If we do not download the unidic in advance, fugashi will output the following error message.
```
RuntimeError:
Failed initializing MeCab.
```

If you want to use python scripts of ESPnet ASR for filelist in the `pysctkja` package, please type the following command to solve optional dependency. 
```
python3 -m pip install asr-ja_evalkit[asr]@git+https://git@github.com/ouktlab/asr-ja_evalkit.git
```
Python libraries, such as `torch`, `torchaudio`, and `espnet`, will be installed.  

#### 3. Import "pysctkja" package (not "asr-ja_evalkit")

```
python3
>>> import pysctkja
>>> print(pysctkja.__version__)
0.1
```

### Run package command
We can run directly `pyscliteja` as command instead of `pyscliteja.py` after pip istall.
```
pyscliteja
usage: pyscliteja [-h] [--scorefile SCOREFILE] [--charnorm CHARNORM]
                  [--pre_rulefile PRE_RULEFILE] [--tagger TAGGER]
                  [--disable_adjust] [--trnfmt TRNFMT]
                  [--post_rulefile POST_RULEFILE] [--ref_pre REF_PRE]
                  [--hyp_pre HYP_PRE] [--ref_adj REF_ADJ] [--hyp_adj HYP_ADJ]
                  [--ref_lemma REF_LEMMA] [--hyp_lemma HYP_LEMMA]
                  ref_list hyp_list ref_trn hyp_trn
pyscliteja: error: the following arguments are required: ref_list, hyp_list, ref_trn, hyp_trn
```

For example, after preparing the "sample" directory, we can calculate CER by the following command. 
```
pyscliteja sample/egs_reflist.txt sample/egs_hyplist.txt sample/ref_trn.txt sample/hyp_trn.txt --scorefile sample/score_with_normalize.txt
```



## Evaluation examples
### Patterns
Our sample scripts output three types of CERs: 
- CER of raw text 
- CER of normalized text using fugashi (objective processing)
- CER of normalized text using rules + fugashi (rules may be subjective)

Data set used for evaluation examples are as follows:
- [SPREDS-D1](https://ast-astrec.nict.go.jp/release/SPREDS-D1/) (NICT ASTREC. License - CC BY 4.0)
   - discourse speech (human-human)
   - many fillers are included
   - segmented data are used
- [SPREDS-D2](https://ast-astrec.nict.go.jp/release/SPREDS-D2/) (NICT ASTREC. License - CC BY 4.0)
   - discourse speech (human-human)
   - many fillers are included
   - segmented data are used
   - long audio files (over 30 sec.) are segmented in advance
- [SPREDS-P1](https://ast-astrec.nict.go.jp/release/SPREDS-P1/) (NICT ASTREC. License - CC BY 4.0)
   - presentation speech
   - segmented data are used
- [SPREDS-U1](https://ast-astrec.nict.go.jp/release/SPREDS-U1/) (NICT ASTREC. License - CC BY 4.0)
   - isolated utterance
- [JSUT](https://sites.google.com/site/shinnosuketakamichi/publication/jsut) (S. Takamichi. License of tags - CC-BY-SA 4.0, audio data is only for research by academic institutions, non-commercial research, and personal use) (modified)
- [JVNV](https://sites.google.com/site/shinnosuketakamichi/research-topics/jvnv_corpus) (CC BY-SA 4.0)
   - emotional speech
- [CPJD](https://sites.google.com/site/shinnosuketakamichi/research-topics/cpjd_corpus) (CC BY-SA 4.0)
   - dialect speech
   - different audio conditions (e.g. strong noise supression)
- CSJ (please purchase this corpus)
   - lecture speech
   - many technical terms: acoustic signal processing and lanugage processing
   - many fillers are included
   - assume eval1, eval2 and eval3 sets built by ESPnet CSJ recipe
- SPREDS-U1-REVBGN
   - synthesized noisy and reverberant speech (artifical data. not natural mixture and situation.)
   - source speech: SPREDS-U1, impulse response: largeroom1 (near and far) from [SLR28](https://openslr.trmal.net/28/), noise: [ESC-50](https://github.com/karolpiczak/ESC-50.git)


Some datasets are automatically downloaded in the shell scripts. 

Sample ASR models are as follows:
- ESPnet models (character-based ASR): standard transformer models trained in our [lab](https://github.com/ouktlab/espnet_asr_models).
   - ESPnet(CSJ core) -- (core set: 220 hrs. paired data)
   - ESPnet(CSJ full) -- (full except D*: 660 hrs. paired data)
   - ESPnet(Corpus10) -- (900 hrs. seed paired data)
      - JSUT is semi-closed set for Corpus10 model (jvs corpus used for training)
- Syllable-ASR & syllable-to-character translation: standard transformer models trained in our [lab](https://github.com/ouktlab/espnet_asr_models).
   - SASR+SCT(Corpus10) -- (900 hrs. seed paired data): 1-best search = cascaded process
      - JSUT is semi-closed set for Corpus10 model (jvs corpus used for training)
      - Same training data with the character-based ASR ESPnet(Corpus10)
- ESPnet models (character-based ASR) for streaming: trained in our [lab](https://github.com/ouktlab/espnet_asr_models).
   - ESPnet-st(Corpus10) (0.25 sec. segment in inference)
      - JSUT is semi-closed set for Corpus10 model (jvs corpus used for training)
- ESPnet models (character-based ASR) 
   - ESPnet([Laborotv](https://huggingface.co/espnet/Shinji_Watanabe_laborotv_asr_train_asr_conformer2_latest33_raw_char_sp_valid.acc.ave))
   - ESPnet([CSJ full,con](https://huggingface.co/ouktlab/espnet_csj_asr_train_asr_conformer_lm_rnn)) -- (full except D*: 660hrs. paired data): conformer model trained in our lab
- Reazon speech
- FunASR (SenseVoiceSmall)
- Whisper (large-v3)
- Nue (not avairable: 2025/12)
- Kotoba Whisper v2.0
- Kushinada


*Rules* were added by checking CER results of ASR models. The order of the check is Whisper, Nue, Reazon, ESPnet, and SASR-SCT.


Score weights (such as CTC, Decoder, and LM) are not optimized for each data set. 


### Summary of CER 
CERs difference between `raw text` and `with fugashi` sometimes become 3~5 points.
Because dialogue corpora includes many fillers, their deletion errors affect CERs of some ASR models.  

Note that these results will slightly change after updates of this toolkit.   
Because the reference text is also modified (such as numbers, words in *rules*), the total number of characters also change.


*Rules* may be added and refined in the future. 

#### Raw text

```
asr-ja_evalkit$ cat result/summary_score_charnorm-v1_rawtext.txt
```

| CER (%)                 |      cpjd |       csj |      jsut |      jvnv | spreds-d1 | spreds-d2 | spreds-p1 | spreds-u1 |spreds-u1-revbgn |
| ---                     | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      |
| 01:ESPnet(CSJ core)     |     32.50 |      6.32 |     21.00 |     26.23 |     17.11 |     28.94 |     18.34 |     19.28 |     43.57 |
| 02:ESPnet(CSJ full)     |     24.19 |      4.05 |     12.29 |     12.76 |     14.50 |     21.95 |     15.05 |      9.21 |     34.83 |
| 03:ESPnet(Corpus10)     |     18.54 |      3.76 |      6.78 |     10.07 |     10.56 |     17.01 |      5.24 |      5.63 |      7.17 |
| 04:SASR+SCT(Corpus10)   |     16.33 |      4.02 |      6.18 |      9.69 |     10.33 |     17.02 |      5.24 |      4.80 |      6.20 |
| 11:ESPnet-st(Corpus10)  |     22.23 |      4.37 |      8.84 |     17.71 |     13.27 |     19.55 |      7.06 |      7.11 |     10.26 |
| 21:ESPnet(Laborotv)     |     17.22 |     19.69 |     11.06 |     11.33 |     20.98 |     28.95 |     12.84 |      7.88 |     24.79 |
| 22:Whisper(large-v3)    |     12.06 |     17.34 |      6.87 |      7.05 |     17.43 |     19.96 |      4.96 |      4.79 |      5.91 |
| 23:Nue                  |       --- |     29.05 |      8.76 |       --- |     25.50 |     31.66 |      7.95 |      5.43 |       --- |
| 24:Reazon               |     12.55 |     18.47 |      6.85 |     28.08 |     15.87 |     20.07 |      3.25 |      4.77 |      5.97 |
| 25:FunASR               |     14.56 |     13.71 |      7.89 |      6.09 |     13.58 |     20.36 |      3.52 |      5.43 |      6.83 |
| 26:Kotoba-whisper(v2.0) |     12.73 |     19.74 |      8.01 |      6.10 |     17.83 |     25.11 |      5.77 |      5.14 |      6.55 |
| 27:Kushinada            |     13.83 |      3.53 |      9.88 |     17.60 |     17.13 |     25.06 |      9.77 |     13.08 |     39.82 |
| 31:ESPnet(CSJ full,con) |     24.86 |      3.81 |     12.13 |     15.14 |     18.80 |     28.05 |     17.34 |     12.67 |     43.75 |


|                         |      cpjd |       csj |      jsut |      jvnv | spreds-d1 | spreds-d2 | spreds-p1 | spreds-u1 |spreds-u1-revbgn |
| ---                     | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      |
| # of characters         |    139127 |    115744 |    205375 |     56987 |     49406 |     23099 |      9747 |     26360 |    158160 |

#### with Fugashi
```
asr-ja_evalkit$ cat result/summary_score_charnorm-v1_fugashi-v1_rule-none.txt
```

| CER (%)                 |      cpjd |       csj |      jsut |      jvnv | spreds-d1 | spreds-d2 | spreds-p1 | spreds-u1 |spreds-u1-revbgn |
| ---                     | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      |
| 01:ESPnet(CSJ core)     |     28.01 |      5.72 |     17.08 |     22.91 |     13.65 |     26.20 |     15.13 |     16.46 |     41.37 |
| 02:ESPnet(CSJ full)     |     18.67 |      3.57 |      7.91 |      9.24 |     10.98 |     18.82 |     12.03 |      6.01 |     32.32 |
| 03:ESPnet(Corpus10)     |     13.29 |      3.25 |      3.53 |      7.26 |      6.88 |     13.97 |      2.76 |      3.07 |      4.57 |
| 04:SASR+SCT(Corpus10)   |     11.25 |      3.44 |      2.24 |      6.37 |      7.08 |     14.12 |      2.48 |      1.69 |      3.21 |
| 11:ESPnet-st(Corpus10)  |     16.77 |      3.71 |      4.82 |     12.20 |      9.86 |     16.45 |      4.05 |      4.11 |      7.36 |
| 21:ESPnet(Laborotv)     |     12.17 |     16.75 |      6.00 |      6.10 |     18.76 |     27.04 |     10.20 |      5.75 |     23.03 |
| 22:Whisper(large-v3)    |      8.36 |     13.31 |      3.63 |      5.35 |     15.99 |     18.17 |      3.49 |      2.00 |      3.11 |
| 23:Nue                  |       --- |     25.50 |      4.43 |       --- |     24.03 |     29.72 |      6.17 |      2.38 |       --- |
| 24:Reazon               |      7.98 |     14.21 |      3.09 |     10.06 |     13.99 |     17.38 |      1.30 |      1.52 |      2.72 |
| 25:FunASR               |     11.16 |     10.95 |      5.07 |      4.97 |     11.93 |     18.65 |      2.20 |      2.86 |      4.37 |
| 26:Kotoba-whisper(v2.0) |      8.98 |     16.07 |      4.76 |      4.15 |     16.49 |     23.56 |      4.16 |      2.41 |      3.83 |
| 27:Kushinada            |      8.17 |      2.97 |      4.13 |      8.51 |     14.67 |     23.03 |      7.32 |     10.78 |     38.39 |
| 31:ESPnet(CSJ full,con) |     19.42 |      3.27 |      7.74 |     11.74 |     15.42 |     25.00 |     14.28 |      9.57 |     41.53 |


|                         |      cpjd |       csj |      jsut |      jvnv | spreds-d1 | spreds-d2 | spreds-p1 | spreds-u1 |spreds-u1-revbgn |
| ---                     | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      |
| # of characters         |    139137 |    115672 |    205449 |     56987 |     49408 |     23103 |      9747 |     26382 |    158292 |


#### with Rules + Fugashi
```
asr-ja_evalkit$ cat result/summary_score_charnorm-v1_fugashi-v1_rule-lax.txt
```

| CER (%)                 |      cpjd |       csj |      jsut |      jvnv | spreds-d1 | spreds-d2 | spreds-p1 | spreds-u1 |spreds-u1-revbgn |
| ---                     | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      |
| 01:ESPnet(CSJ core)     |     28.01 |      5.64 |     17.04 |     22.91 |     12.16 |     26.03 |     15.16 |     16.22 |     41.23 |
| 02:ESPnet(CSJ full)     |     18.67 |      3.51 |      7.86 |      9.22 |      9.39 |     18.62 |     12.07 |      5.68 |     32.14 |
| 03:ESPnet(Corpus10)     |     13.29 |      3.20 |      3.47 |      7.25 |      5.31 |     13.75 |      2.70 |      2.63 |      4.22 |
| 04:SASR+SCT(Corpus10)   |     11.25 |      3.36 |      2.17 |      6.33 |      5.39 |     13.90 |      2.51 |      1.32 |      2.89 |
| 11:ESPnet-st(Corpus10)  |     16.77 |      3.68 |      4.74 |     12.17 |      8.43 |     16.29 |      4.02 |      3.70 |      6.99 |
| 21:ESPnet(Laborotv)     |     12.17 |     16.43 |      5.92 |      6.07 |     18.34 |     26.96 |      9.98 |      5.33 |     22.71 |
| 22:Whisper(large-v3)    |      8.36 |     12.75 |      3.52 |      3.97 |     14.74 |     18.02 |      3.18 |      1.43 |      2.58 |
| 23:Nue                  |       --- |     25.10 |      4.34 |       --- |     23.66 |     29.55 |      5.94 |      1.84 |       --- |
| 24:Reazon               |      7.98 |     13.71 |      3.00 |     10.06 |     13.54 |     17.25 |      1.04 |      1.06 |      2.28 |
| 25:FunASR               |     11.16 |     10.30 |      4.99 |      4.95 |     11.49 |     18.56 |      1.96 |      2.48 |      4.07 |
| 26:Kotoba-whisper(v2.0) |      8.98 |     15.69 |      4.67 |      4.13 |     16.09 |     23.42 |      3.95 |      1.88 |      3.32 |
| 27:Kushinada            |      8.17 |      2.91 |      4.05 |      8.50 |     13.91 |     22.92 |      7.06 |     10.41 |     38.11 |
| 31:ESPnet(CSJ full,con) |     19.42 |      3.22 |      7.69 |     11.72 |     13.93 |     24.83 |     14.28 |      9.21 |     41.36 |


|                         |      cpjd |       csj |      jsut |      jvnv | spreds-d1 | spreds-d2 | spreds-p1 | spreds-u1 |spreds-u1-revbgn |
| ---                     | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      | ---:      |
| # of characters         |    139137 |    115676 |    205483 |     56997 |     49377 |     23119 |      9747 |     26378 |    158268 |
