#!/bin/bash
source "/data/Personal-Medical-Assistant/backend/content_extractor/preprocessing_venv/bin/activate"
python3 -u /data/Personal-Medical-Assistant/backend/content_extractor/preprocessing.py > preprocessing.out
deactivate

echo "FIRST PART DONE!"

source "/data/Personal-Medical-Assistant/backend/content_extractor/ocr_venv/bin/activate"
python3 -u /data/Personal-Medical-Assistant/backend/content_extractor/ocr.py > ocr.out
deactivate

echo "SECOND PART DONE!"

source "/data/Personal-Medical-Assistant/backend/content_extractor/postprocessing_venv/bin/activate"
python3 -u /data/Personal-Medical-Assistant/backend/content_extractor/postprocessing.py > postprocessing.out
deactivate

echo "THIRD PART DONE!"
