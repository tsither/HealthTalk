#!/bin/bash
echo  "Preprocessing!"

source "/data/Personal-Medical-Assistant/backend/content_extractor/preprocessing_venv/bin/activate"
python3 -u /data/Personal-Medical-Assistant/backend/content_extractor/preprocessing.py > ./logs/preprocessing.out
deactivate

echo "OCR!"

source "/data/Personal-Medical-Assistant/backend/content_extractor/ocr_venv/bin/activate"
python3 -u /data/Personal-Medical-Assistant/backend/content_extractor/ocr.py > ./logs/ocr.out
deactivate


echo "Postprocessing!"

source "/data/Personal-Medical-Assistant/backend/content_extractor/postprocessing_venv/bin/activate"
python3 -u /data/Personal-Medical-Assistant/backend/content_extractor/postprocessing.py > ./logs/postprocessing.out
deactivate

echo "Evaluating!"

source "/data/Personal-Medical-Assistant/backend/content_extractor/evaluate_venv/bin/activate"
python3 -u /data/Personal-Medical-Assistant/backend/content_extractor/evaluate.py > ./logs/evaluation.out
deactivate


echo "Testing done!"

