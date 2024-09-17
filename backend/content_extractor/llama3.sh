#!/bin/bash
echo "Postprocessing Llama3!"

source "/data/Personal-Medical-Assistant/backend/content_extractor/postprocessing_venv/bin/activate"
python3 -u /data/Personal-Medical-Assistant/backend/content_extractor/postprocessing.py > ./logs/postprocessing_llama3.out
deactivate

echo "DONE Llama3!"