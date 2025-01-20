from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.core.exceptions import ValidationError
from .models import Document
from .serializers import DocumentSerializer
from .utils import extract_text_from_pdf, extract_text_from_image, analyze_text
import os
import logging

logger = logging.getLogger(__name__)


class DocumentUploadView(APIView):
    """
    API endpoint to handle document uploads, extract text, and analyze content.

    Supported file types: PDF, PNG, JPG, JPEG
    """

    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        """
        Handles document uploads, extracts text, and analyzes it.
        """
        file_serializer = DocumentSerializer(data=request.data)

        if not file_serializer.is_valid():
            return Response(
                {"error": "Invalid file format", "details": file_serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Save the uploaded file
        try:
            file_serializer.save()
            file_path = file_serializer.instance.file.path
        except ValidationError as e:
            logger.error(f"Validation error while saving file: {e}")
            return Response({"error": "File validation failed."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error during file saving: {e}")
            return Response({"error": "Internal server error while saving file."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Ensure the file exists on the server
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return Response({"error": "File not found on the server."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Determine file type
        file_type = os.path.splitext(file_path)[-1].lower().replace('.', '')
        supported_types = ['pdf', 'png', 'jpg', 'jpeg']

        if file_type not in supported_types:
            os.remove(file_path)
            return Response({"error": "Unsupported file type. Please upload a PDF, PNG, or JPG file."},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            # Extract text based on file type
            text = extract_text_from_pdf(
                file_path) if file_type == 'pdf' else extract_text_from_image(file_path)

            if not text.strip():
                os.remove(file_path)
                return Response({"error": "Failed to extract readable text from the file."},
                                status=status.HTTP_400_BAD_REQUEST)

            # Analyze extracted text
            analysis_result = analyze_text(text)

            return Response(
                {
                    "message": "File processed successfully.",
                    "text": text,
                    "analysis": analysis_result
                },
                status=status.HTTP_201_CREATED
            )

        except ValueError as e:
            logger.error(f"Value error during processing: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f"Unexpected error during processing: {e}")
            return Response({"error": "An unexpected error occurred during processing."},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)
