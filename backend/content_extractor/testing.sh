#!/bin/bash
echo "Postprocessing!"

source "/data/Personal-Medical-Assistant/backend/content_extractor/postprocessing_venv/bin/activate"
python3 -u /data/Personal-Medical-Assistant/backend/content_extractor/postprocessing.py > ./logs/postprocessing.out
deactivate

echo "Postprocessing done!"

echo "Evaluating!"

source "/data/Personal-Medical-Assistant/backend/content_extractor/evaluate_venv/bin/activate"
python3 -u /data/Personal-Medical-Assistant/backend/content_extractor/evaluate.py > ./logs/evaluate.out
deactivate

echo "Testing done!"

