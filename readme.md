# HealthTalk

HealthTalk is an application to upload and query personal medical information using large language models. 

## Usage

Navigate to the following directory:


```bash
HealthTalk/desktop_app/manage.py
```

Then, 

- In the process_reports function (Healthtalk/desktop_app/ui/views/py) and in page3_view you’ll need to set your python version:
    - either python3 or python

Finally, 

run the following Django file along with the appropriate arguments to start the application.

```bash
python manage.py runserver
```
Follow the link to begin the server.

```bash
Django version 5.1, using settings 'desktop_app.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```
## Desktop app

Our product integrated in a locally run web-based Django application. 

The logic of the application is contain in 'views.py' located here:

```bash
Personal-Medical-Assistant/desktop_app/ui/views.py
```

## Dependencies

1. Install Python Requirements:
Install required packages by running:
    
    ```bash
    pip install -r requirements.txt
    
    ```
    
2. Install External Libraries:
    - [Poppler](https://pdf2image.readthedocs.io/en/latest/installation.html#installing-poppler) - Required for PDF processing.
    - [Tesseract](https://tesseract-ocr.github.io/tessdoc/Installation.html) - Needed for Optical Character Recognition (OCR).
   
## Testing and Evaluation


### Content Extractor

Contains the logic (and testing) of the content extractor feature. 
Sample reports are available at:
- ~/HealthTalk/backend_testing/content_extractor/data/images

### Fine-tuning
Contains files related to the formatting of the [Spider](https://yale-lily.github.io/spider) dataset.

### LLM Agent
Contains the files in which responses to the test datasets are generated and evaluated. 

## License

Nobody touches, looks at, or smells this without asking. 
