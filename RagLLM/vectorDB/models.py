import io
import re
import unicodedata
from django.db import models
from django.core.validators import FileExtensionValidator
from pypdf import PdfReader

# from ..User.models import User
from User.models import User


# Create your models here.
class Document(models.Model):
    owned_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="documents"
    )
    # Store PDF content as binary data
    file_data = models.BinaryField(null=True, blank=True)
    file_name = models.CharField(max_length=255, null=True, blank=True)
    file_size = models.PositiveIntegerField(null=True, blank=True)
    content = models.TextField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.file_data and not self.content:
            self.extractTextFromPdf()
            print(self.content)
        super().save(*args, **kwargs)

    def extractTextFromPdf(self):
        text = ""
        try:
            # Create a BytesIO object from the binary data
            pdf_file = io.BytesIO(self.file_data)
            pdf = PdfReader(pdf_file)
            for page in pdf.pages:
                text += page.extract_text()
        except Exception as e:
            text = ""
        self.content = self.preprocess_text_for_rag(text)

    def preprocess_text_for_rag(self, text):
        """
        Preprocess text content to optimize it for RAG applications
        """
        if not text:
            return ""

        # 1. Normalize Unicode characters
        text = unicodedata.normalize("NFKD", text)

        # 2. Remove excessive whitespace and normalize line breaks
        text = re.sub(
            r"\s+", " ", text
        )  # Replace multiple whitespace with single space
        text = re.sub(r"\n\s*\n", "\n\n", text)  # Normalize paragraph breaks

        # 3. Remove page numbers and headers/footers patterns
        # Common page number patterns at start/end of lines
        text = re.sub(r"^\s*\d+\s*$", "", text, flags=re.MULTILINE)
        text = re.sub(r"^\s*Page\s+\d+\s*$", "", text, flags=re.MULTILINE)

        # 4. Remove common PDF artifacts
        text = re.sub(
            r"[^\w\s\.\!\?\,\;\:\(\)\[\]\{\}\'\"\/\-\+\=\@\#\$\%\^\&\*]", "", text
        )

        # 5. Fix common OCR errors and PDF extraction issues
        text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)  # Add space between camelCase
        text = re.sub(r"([a-z])([A-Z])", r"\1 \2", text)  # Split joined words

        # 6. Remove standalone single characters (common OCR artifacts)
        text = re.sub(r"\b[a-zA-Z]\b(?!\s[a-zA-Z]\b)", "", text)

        # 7. Fix punctuation spacing
        text = re.sub(r"\s+([,.!?;:])", r"\1", text)  # Remove space before punctuation
        text = re.sub(r"([,.!?;:])\s*", r"\1 ", text)  # Ensure space after punctuation

        # 8. Clean up multiple spaces again after all processing
        text = re.sub(r"\s+", " ", text)

        # 9. Remove leading/trailing whitespace
        text = text.strip()

        # 10. Ensure proper sentence boundaries for better chunking
        text = re.sub(
            r"\.(?=[A-Z])", ". ", text
        )  # Ensure space after period before capital letter
        text = re.sub(r"\?(?=[A-Z])", "? ", text)  # Ensure space after question mark
        text = re.sub(r"!(?=[A-Z])", "! ", text)  # Ensure space after exclamation mark

        # 11. Remove very short lines that are likely artifacts (less than 3 words)
        lines = text.split("\n")
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if (
                len(line.split()) >= 3 or len(line) == 0
            ):  # Keep empty lines for paragraph breaks
                cleaned_lines.append(line)

        text = "\n".join(cleaned_lines)

        # 12. Final cleanup
        text = re.sub(r"\n\s*\n\s*\n+", "\n\n", text)  # Remove excessive line breaks
        text = text.strip()

        return text

    def get_file_data(self):
        """Return the PDF file data as bytes"""
        return self.file_data

    def get_file_name(self):
        """Return the original filename"""
        return self.file_name or "document.pdf"
