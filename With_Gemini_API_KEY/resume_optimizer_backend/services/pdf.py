# import PyPDF2
# from io import BytesIO

# class PDFService:
#     @staticmethod
#     def extract_text(pdf_file: bytes) -> str:
#         pdf_reader = PyPDF2.PdfReader(BytesIO(pdf_file))
#         text = ""
#         for page in pdf_reader.pages:
#             text += page.extract_text()
#         return text

import os
import tempfile
from fpdf import FPDF
from datetime import datetime

ACCENT      = (44, 62, 122)
BLACK       = (30, 30, 30)
LIGHT_GRAY  = (120, 120, 120)
PAGE_W      = 210
MARGIN      = 18
CONTENT_W   = PAGE_W - 2 * MARGIN


class ResumePDF(FPDF):
    def header(self):
        pass

    def footer(self):
        self.set_y(-12)
        self.set_font("Times", size=8)
        self.set_text_color(*LIGHT_GRAY)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def _is_section_header(text: str) -> bool:
    t = text.strip()
    return (
        bool(t)
        and t == t.upper()
        and len(t) <= 45
        and not t.startswith(("-", "•", "*", "·"))
        and any(c.isalpha() for c in t)
    )


def _is_bullet(text: str) -> bool:
    return text.strip().startswith(("-", "•", "*", "·"))


def _clean_bullet(text: str) -> str:
    return text.strip().lstrip("-•*· ").strip()


def generate_pdf(optimized_resume: str) -> bytes:
    """Generate a styled PDF from resume text and return raw bytes."""
    pdf = ResumePDF(format="A4")
    pdf.set_margins(MARGIN, MARGIN, MARGIN)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    lines     = optimized_resume.strip().splitlines()
    name_line = ""
    body_start = 0

    for i, line in enumerate(lines):
        if line.strip():
            name_line  = line.strip()
            body_start = i + 1
            break

    contact_line = ""
    contact_indicators = ["|", "•", "@", "linkedin", "github", "+", "http"]
    for i, line in enumerate(lines[body_start:], start=body_start):
        if line.strip():
            if any(ind in line.strip().lower() for ind in contact_indicators):
                contact_line = line.strip()
                body_start   = i + 1
            break

    # Header
    pdf.set_font("Times", style="B", size=22)
    pdf.set_text_color(*ACCENT)
    pdf.cell(0, 10, name_line, new_x="LMARGIN", new_y="NEXT", align="C")

    if contact_line:
        pdf.set_font("Times", size=9)
        pdf.set_text_color(*LIGHT_GRAY)
        pdf.cell(0, 5, contact_line, new_x="LMARGIN", new_y="NEXT", align="C")

    pdf.ln(3)
    pdf.set_draw_color(*ACCENT)
    pdf.set_line_width(0.8)
    pdf.line(MARGIN, pdf.get_y(), PAGE_W - MARGIN, pdf.get_y())
    pdf.ln(5)
    pdf.set_line_width(0.3)

    # Body
    for line in lines[body_start:]:
        stripped = line.strip()

        if not stripped:
            pdf.ln(2)
            continue

        if _is_section_header(stripped):
            pdf.ln(3)
            pdf.set_font("Times", style="B", size=11)
            pdf.set_text_color(*ACCENT)
            pdf.cell(0, 6, stripped, new_x="LMARGIN", new_y="NEXT")
            pdf.set_draw_color(*ACCENT)
            pdf.line(MARGIN, pdf.get_y(), PAGE_W - MARGIN, pdf.get_y())
            pdf.ln(3)

        elif _is_bullet(stripped):
            pdf.set_font("Times", size=10)
            pdf.set_text_color(*BLACK)
            pdf.set_x(MARGIN + 4)
            pdf.cell(4, 5, "•")
            pdf.set_x(MARGIN + 9)
            pdf.multi_cell(CONTENT_W - 9, 5, _clean_bullet(stripped))

        else:
            pdf.set_font("Times", size=10)
            pdf.set_text_color(*BLACK)
            pdf.multi_cell(CONTENT_W, 5, stripped)

    # Return raw bytes (no temp file needed)
    return bytes(pdf.output())