# build_full_ieee_paper.py
"""
Complete 12-Page IEEE Research Paper Generator for AgentShield AI
Target: Exactly 12.0 Pages in IEEE Two-Column Format
Outputs:
  - AgentShield_AI_12_Page_IEEE_Research_Paper.pdf (ReportLab, exact 12 pages)
  - AgentShield_AI_12_Page_IEEE_Research_Paper.docx (python-docx matching Word Document)
"""

import os
import sys
import subprocess
import pypdf
import docx
from docx.shared import Inches as DocxInches, Pt as DocxPt, RGBColor as DocxRGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

import reportlab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, FrameBreak, PageBreak, KeepTogether, HRFlowable, NextPageTemplate
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# ==============================================================================
# 1. IEEE NUMBERED CANVAS WITH RUNNING HEADERS, FOOTERS & PAGE NUMBERS
# ==============================================================================
class IEEENumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, total_pages):
        self.saveState()
        self.setFont('Times-Roman', 7.5)
        self.setFillColor(colors.HexColor('#222222'))
        
        # Running Top Header (IEEE standard format)
        header_text_1 = 'Proceedings of the IEEE International Conference on Cloud Security & Autonomous Systems (ICCSAS-2026)'
        header_text_2 = 'IEEE Xplore Part Number: CFP26CS-ART; ISBN: 979-8-3315-9120-1'
        self.drawString(36, 762, header_text_1)
        self.drawRightString(576, 762, header_text_2)
        self.setStrokeColor(colors.HexColor('#888888'))
        self.setLineWidth(0.5)
        self.line(36, 755, 576, 755)
        
        # Running Bottom Footer
        self.line(36, 32, 576, 32)
        footer_text = f'AgentShield AI: Autonomous Multi-Agent IaC Security Framework — Page {self._pageNumber} of {total_pages}'
        self.drawString(36, 22, footer_text)
        self.drawRightString(576, 22, 'IEEE Trans. Dependable & Secure Comput.')
        self.restoreState()


print("Canvas module ready.")
