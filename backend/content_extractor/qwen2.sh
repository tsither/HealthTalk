#!/bin/bash
echo "Postprocessing Qwen2!"

source "/data/Personal-Medical-Assistant/backend/content_extractor/venv/bin/activate"
python3 -u /data/Personal-Medical-Assistant/backend/content_extractor/postprocessing.py > ./logs/postprocessing_qwen2.out
deactivate

echo "DONE Qwen2!"