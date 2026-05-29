from io import BytesIO

import fitz
from docx import Document
from fastapi import HTTPException, UploadFile, status


class TextExtractor:

    @staticmethod
    async def extract_text(
        file: UploadFile,
    ) -> str:

        filename = (
            file.filename or ""
        ).lower()

        if filename.endswith(".pdf"):
            return await (
                TextExtractor
                ._extract_pdf(file)
            )

        if filename.endswith(".docx"):
            return await (
                TextExtractor
                ._extract_docx(file)
            )

        if filename.endswith(".txt"):
            return await (
                TextExtractor
                ._extract_txt(file)
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Only PDF, DOCX and TXT "
                "files are supported."
            ),
        )

    @staticmethod
    async def _extract_pdf(
        file: UploadFile,
    ) -> str:

        pdf_bytes = await file.read()

        document = fitz.open(
            stream=pdf_bytes,
            filetype="pdf",
        )

        text_parts = []

        for page in document:
            text_parts.append(
                page.get_text()
            )

        document.close()

        return "\n".join(
            text_parts
        ).strip()

    @staticmethod
    async def _extract_docx(
        file: UploadFile,
    ) -> str:

        docx_bytes = await file.read()

        document = Document(
            BytesIO(docx_bytes)
        )

        return "\n".join(
            paragraph.text
            for paragraph in document.paragraphs
        ).strip()

    @staticmethod
    async def _extract_txt(
        file: UploadFile,
    ) -> str:

        text_bytes = await file.read()

        return text_bytes.decode(
            "utf-8",
            errors="ignore",
        ).strip()