#!/bin/bash
source "/data/Personal-Medical-Assistant/backend/content_extractor/preprocessing_venv/bin/activate"
python3 -u /data/Personal-Medical-Assistant/backend/content_extractor/preprocessing.py > preprocessing.out
deactivate

source "/data/Personal-Medical-Assistant/backend/content_extractor/ocr_venv/bin/activate"
python3 -u /data/Personal-Medical-Assistant/backend/content_extractor/ocr.py > ocr.out
deactivate

source "/data/Personal-Medical-Assistant/backend/content_extractor/postprocessing_venv/bin/activate"
python3 -u /data/Personal-Medical-Assistant/backend/content_extractor/postprocessing.py > postprocessing.out
deactivate

echo "DONE!"