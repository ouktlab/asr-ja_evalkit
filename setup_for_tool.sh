###
stage=0

###
python=python3 # python3.10, python3.11

###
if [ $stage -le 0 ]; then
    sudo apt install sctk
fi

if [ $stage -le 1 ]; then
    ${python} -m venv venv/fugashi
    . venv/fugashi/bin/activate
    ${python} -m pip install 'fugashi[unidic]' pyyaml
    ${python} -m unidic download
    deactivate
fi


