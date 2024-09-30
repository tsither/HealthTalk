#!/bin/bash
echo "Postprocessing Phi3!"

source "/data/Personal-Medical-Assistant/backend/content_extractor/venv/bin/activate"
python3 -u /data/Personal-Medical-Assistant/backend/content_extractor/postprocessing.py > ./logs/postprocessing_phi3.out
deactivate

echo "DONE Phi3!"