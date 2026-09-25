"""
build_impact_crc.py
Generates the extended Camera-Ready Copy (CRC) Word manuscript (.docx) and PDF
for AgentShield AI, ensuring comprehensive publication-grade depth (>12 pages).
"""

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_PAPER_DIR = os.path.join(BASE_DIR, "docs", "paper")
sys.path.insert(0, os.path.dirname(__file__))

from build_extended_crc import generate_extended_paper, convert_to_pdf, DOCX_OUT, PDF_OUT


def build_manuscript(output_path):
    generate_extended_paper(output_path)


if __name__ == "__main__":
    target1 = os.path.join(DOCS_PAPER_DIR, "CRC_AgentShield_AI.docx")
    target2 = os.path.join(DOCS_PAPER_DIR, "CRC_549.docx")
    target3 = os.path.join(BASE_DIR, "CRC_AgentShield_AI.docx")
    
    build_manuscript(target1)
    build_manuscript(target2)
    build_manuscript(target3)
    
    pages = convert_to_pdf()
    print(f"Generated CRC Manuscript across targets. Resulting PDF Page Count: {pages}")
