###
stage=0

###
espnet=true
whisper=true
reazon=true
nue=true
funasr=true
fugashi=true
kotobaw=true
kushinada=true
qwen=true

###
fleurs=true

###
python=python3 # python3.10, python3.11

###
if [ $stage -le 0 ]; then
  sudo apt install ffmpeg sctk
fi

if "${espnet}"; then
    echo "-- espnet ------- "
    sudo apt install -y ${python}-venv ${python}-dev
    
    ${python} -m venv venv/espnet/
    . venv/espnet/bin/activate
    ${python} -m pip install --upgrade pip
    ${python} -m pip install espnet torchaudio torchcodec transformers soxr
    ${python} -m pip install -U espnet_model_zoo
    deactivate
fi

if "${whisper}"; then
    echo "-- whilsper ------- "
    ${python} -m venv venv/whisper
    . venv/whisper/bin/activate
    ${python} -m pip install -U openai-whisper
    deactivate
fi

if "${reazon}"; then
    echo "-- reazon ------- "
    git clone https://github.com/reazon-research/ReazonSpeech
    ${python} -m venv venv/reazon
    . venv/reazon/bin/activate
    ${python} -m pip install Cython
    ${python} -m pip install ReazonSpeech/pkg/espnet-asr
    
    # do if numpy version is different
    ${python} -m pip uninstall numpy
    ${python} -m pip install numpy==1.23
    deactivate
fi

if "${nue}"; then
    echo "-- nue ------- "
    ${python} -m venv venv/nue
    . venv/nue/bin/activate
    ${python} -m pip install git+https://github.com/rinnakk/nue-asr.git
    ${python} -m pip install sentencepiece
    deactivate
fi

if [ "${funasr}" ]; then
    echo "-- funasr ------- "
    ${python} -m venv venv/funasr/
    . venv/funasr/bin/activate
    ${python} -m pip install --upgrade pip
    ${python} -m pip install -U funasr torch torchaudio torchcodec transformers
    deactivate
fi

if "${kotobaw}"; then
    echo "-- kotoba-whisper-v2.0 ------- "
    ${python} -m venv venv/kotobaw
    . venv/kotobaw/bin/activate
    ${python} -m pip install -U torch transformers torchaudio
    deactivate
fi

if "${kushinada}"; then
    echo "-- kushinada ------- "
    ${python} -m venv venv/kushinada
    . venv/kushinada/bin/activate
    ${python} -m pip install -U espnet==202402 torch==2.2.0 torchaudio==2.2.0 soxr s3prl espnet_model_zoo
    deactivate
fi

if "${fugashi}"; then
    echo "-- fugashi ------- "
    ${python} -m venv venv/fugashi
    . venv/fugashi/bin/activate
    ${python} -m pip install 'fugashi[unidic]' pyyaml
    ${python} -m unidic download
    deactivate
fi

if "${fleurs}"; then
    echo "-- fleurs dataset"
    ${python} -m venv venv/fleurs
    . venv/fleurs/bin/activate
    ${python} -m pip install datasets==3.6.0 soundfile librosa
    deactivate
fi

if "${qwen}"; then
    echo "-- qwen-asr"
    ${python} -m venv venv/qwen
    . venv/qwen/bin/activate
    ${python} -m pip install numpy typing_extensions
    ${python} -m pip install qwen-asr
    deactivate
fi
