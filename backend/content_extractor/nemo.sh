#!/bin/bash
echo "Postprocessing Nemo!"

source "/data/Personal-Medical-Assistant/backend/content_extractor/venv/bin/activate"
python3 -u /data/Personal-Medical-Assistant/backend/content_extractor/postprocessing.py > ./logs/postprocessing_nemo.out
deactivate

echo "DONE Nemo!"