# Content Analyzer Backend

This is the backend for the **Content Analyzer** project, which allows users to upload documents (PDFs and images), extract text, and perform sentiment analysis and keyword extraction.

## Project Links

- **Frontend :** [ Live Application url ](https://content-analyzer-unthinkable.netlify.app/)

## Features

- **File Upload:** Supports PDF, PNG, JPG, and JPEG.
- **Text Extraction:** 
  - PDFs: `pdfplumber` (fallback to `pdfminer`)
  - Images: `Tesseract OCR`
- **Text Analysis:** Keywords and sentiment analysis via `spaCy` and `TextBlob`.
- **CORS Support:** Secure communication with frontend.
- **Automatic File Cleanup:** Deletes processed files.

## API Endpoints
- **Upload Document:** POST /api/upload/
- Uploads a file and returns extracted text and analysis.

### Example Request (cURL)
```bash
curl -X POST "https://content-analyzer-production.up.railway.app/api/upload/" \
     -F "file=@sample.pdf"
```

### Example Response
```bash
{
  "message": "File processed successfully.",
  "text": "Extracted text from the document...",
  "analysis": {
    "keywords": ["analysis", "document", "text"],
    "sentiment": "Positive"
  }
}
```

## Deployment
The project is deployed on Railway.app with the frontend hosted on Netlify.

## Technologies Used
- Django REST Framework
- spaCy, TextBlob, Tesseract OCR
- PostgreSQL, Whitenoise, CORS Headers
- **Deployment:** Railway.app, Netlify


## Contact:

- Aryan Gupta - aryan014kumar@gmail.com
