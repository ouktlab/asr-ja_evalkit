stage=0

if [ $stage -le 0 ]; then
    . ../venv/fleurs/bin/activate
    
    mkdir -p audio/
    mkdir -p list/
    python3 dl.py

    deactivate
fi
