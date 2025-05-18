from django.db import models
from django.core.validators import FileExtensionValidator
from pypdf import PdfReader
from ..User.models import User


# Create your models here.
class Document(models.Model):
    owned_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="documents", unique=False
    )
    file = models.FileField(
        upload_to="pdfs/",
        null=True,
        blank=True,
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
    )
    extracted_text = models.TextField(null=True, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.file and not self.extracted_text:
            self.extractTextFromPdf()
        super().save(self, *args, **kwargs)

    def extractTextFromPdf(self):
        text = ""
        try:
            with self.file.open("rb") as f:
                pdf = PdfReader(f)
                for page in pdf.page:
                    text += page.extract_text()
        except Exception as e:
            text = ""
        return text
