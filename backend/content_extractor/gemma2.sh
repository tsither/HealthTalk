#!/bin/bash
echo "Postprocessing Gemma2!"

source "/data/Personal-Medical-Assistant/backend/content_extractor/venv/bin/activate"
python3 -u /data/Personal-Medical-Assistant/backend/content_extractor/postprocessing.py > ./logs/postprocessing_gemma2.out
deactivate

echo "DONE Gemma2!"