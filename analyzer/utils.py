import pdfplumber
from pdfminer.high_level import extract_text as pdfminer_extract_text
import pytesseract
from PIL import Image
import spacy
import logging
from spacy.tokens import Doc
from textblob import TextBlob

logger = logging.getLogger(__name__)

# Load spaCy model for text analysis
nlp = spacy.load("en_core_web_sm")


if not Doc.has_extension("polarity"):
    Doc.set_extension("polarity", getter=lambda doc: TextBlob(
        doc.text).sentiment.polarity)


def extract_text_from_pdf(file_path):
    """
    Extracts text from a PDF file while maintaining formatting as accurately as possible.
    Uses pdfplumber with optimized tolerances and falls back to pdfminer for stubborn cases.
    """
    text = ""

    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # Fine-tuned tolerance values for better layout preservation
                page_text = page.extract_text(
                    x_tolerance=0.5, y_tolerance=0.5, layout=True)
                if page_text:
                    text += page_text + "\n\n"

        # If no text was extracted, try pdfminer as a fallback
        if not text.strip():
            logger.warning(f"Falling back to pdfminer for: {file_path}")
            text = pdfminer_extract_text(file_path)

        if not text.strip():
            raise ValueError(
                "Text extraction failed. The PDF might be scanned or encrypted.")

    except Exception as e:
        logger.error(f"Error extracting text from PDF {file_path}: {e}")
        raise RuntimeError(f"Failed to extract text from PDF: {str(e)}")

    return text.strip()


def extract_text_from_image(file_path):
    """
    Extracts text from an image file using Tesseract OCR.
    Optimizes image preprocessing for better OCR accuracy.
    """
    try:
        img = Image.open(file_path)

        # Convert to grayscale and apply adaptive thresholding for better OCR
        img = img.convert('L')
        img = img.point(lambda x: 0 if x < 140 else 255, '1')

        text = pytesseract.image_to_string(img, config="--psm 6")
        return text.strip()
    except Exception as e:
        logger.error(f"Error extracting text from image {file_path}: {e}")
        return None


def analyze_text(text):
    """
    Analyzes text using spaCy for keyword extraction and sentiment analysis.
    """
    doc = nlp(text)

    # Extract meaningful keywords (excluding stopwords, punctuation)
    keywords = {
        token.lemma_ for token in doc if token.is_alpha and not token.is_stop}

    # Use the registered extension for sentiment analysis
    polarity = doc._.polarity

    sentiment = "Positive" if polarity > 0 else "Negative" if polarity < 0 else "Neutral"

    return {
        "keywords": list(keywords),
        "sentiment": sentiment
    }
