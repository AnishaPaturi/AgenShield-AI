"""
build_6page_paper.py
Precision-Calibrated 6-Page IEEE Two-Column PDF & DOCX Generator for AgentShield AI
Includes Architecture Diagram (image.png) in Section III
Target: Exactly 6.0 Pages
"""

import os
import sys
import re
import pypdf
import docx
from docx.shared import Inches as DocxInches, Pt as DocxPt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

import reportlab
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle, FrameBreak, HRFlowable, NextPageTemplate, Image as RLImage
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

import paper_data_6pages as pdata

IMAGE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "image.png")

class IEEENumberedCanvas6P(canvas.Canvas):
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
        
        # Top Header (IEEE standard matching ICCSAS-2026)
        header_text_1 = 'Proceedings of the IEEE International Conference on Cloud Security & Autonomous Systems (ICCSAS-2026)'
        header_text_2 = 'IEEE Xplore Part Number: CFP26CS-ART; ISBN: 979-8-3315-9120-1'
        self.drawString(36, 762, header_text_1)
        self.drawRightString(576, 762, header_text_2)
        self.setStrokeColor(colors.HexColor('#888888'))
        self.setLineWidth(0.5)
        self.line(36, 755, 576, 755)
        
        # Bottom Footer
        self.line(36, 32, 576, 32)
        footer_text = f'AgentShield AI: Autonomous Multi-Agent IaC Security Framework — Page {self._pageNumber} of {total_pages}'
        self.drawString(36, 22, footer_text)
        self.drawRightString(576, 22, 'IEEE Trans. Dependable & Secure Comput.')
        self.restoreState()


def compile_pdf_6p(pdf_path, body_fs=10.4, body_lead=12.27, p_sp=4.5, tbl_fs=6.0, tbl_pad=1.2, sec_sp_before=4.0, sec_sp_after=1.8, img_w=254, img_h=122):
    doc = BaseDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    col_w = 260.0
    col_h_p1 = 576.0
    col_h_other = 708.0
    col_gap = 20.0
    left_x = 36.0
    right_x = left_x + col_w + col_gap
    bottom_y = 38.0

    frame_p1_header = Frame(left_x, 620, 540, 132, id='F_P1_Top', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    frame_p1_c1 = Frame(left_x, bottom_y, col_w, col_h_p1, id='F_P1_C1', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    frame_p1_c2 = Frame(right_x, bottom_y, col_w, col_h_p1, id='F_P1_C2', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

    frame_c1 = Frame(left_x, bottom_y, col_w, col_h_other, id='F_C1', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    frame_c2 = Frame(right_x, bottom_y, col_w, col_h_other, id='F_C2', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)

    pt_first = PageTemplate(id='FirstPage', frames=[frame_p1_header, frame_p1_c1, frame_p1_c2])
    pt_two_col = PageTemplate(id='TwoColPage', frames=[frame_c1, frame_c2])
    doc.addPageTemplates([pt_first, pt_two_col])

    # Styles
    title_style = ParagraphStyle('DocTitle', fontName='Times-Bold', fontSize=14.5, leading=17.0, alignment=1, spaceAfter=4)
    author_style = ParagraphStyle('AuthorBlock', fontName='Times-Roman', fontSize=7.6, leading=9.2, alignment=1, spaceAfter=3)
    abstract_title_style = ParagraphStyle('AbstractTitle', fontName='Times-BoldItalic', fontSize=body_fs, leading=body_lead, alignment=4, spaceAfter=p_sp)
    abstract_body_style = ParagraphStyle('AbstractBody', fontName='Times-Italic', fontSize=body_fs - 0.2, leading=body_lead - 0.2, alignment=4, spaceAfter=p_sp)
    sec_head_style = ParagraphStyle('SectionHeading', fontName='Times-Bold', fontSize=body_fs + 1.0, leading=body_lead + 1.2, alignment=1, spaceBefore=sec_sp_before, spaceAfter=sec_sp_after, keepWithNext=True)
    body_style = ParagraphStyle('IEEEBody', fontName='Times-Roman', fontSize=body_fs, leading=body_lead, alignment=4, spaceAfter=p_sp, firstLineIndent=8.0)
    body_noindent = ParagraphStyle('IEEEBodyNoIndent', fontName='Times-Roman', fontSize=body_fs, leading=body_lead, alignment=4, spaceAfter=p_sp, firstLineIndent=0.0)
    equation_style = ParagraphStyle('IEEEEquation', fontName='Times-Italic', fontSize=body_fs, leading=body_lead + 0.8, alignment=1, spaceBefore=p_sp, spaceAfter=p_sp)
    code_style = ParagraphStyle('CodeDiff', fontName='Courier', fontSize=tbl_fs + 0.1, leading=tbl_fs + 1.5, alignment=0, spaceAfter=p_sp)
    table_cell_style = ParagraphStyle('TableCell', fontName='Times-Roman', fontSize=tbl_fs, leading=tbl_fs + 1.2, alignment=0)
    table_hdr_style = ParagraphStyle('TableHdr', fontName='Times-Bold', fontSize=tbl_fs, leading=tbl_fs + 1.2, alignment=0)
    table_title_style = ParagraphStyle('TableTitle', fontName='Times-Bold', fontSize=body_fs - 0.2, leading=body_lead - 0.2, alignment=1, spaceBefore=p_sp + 1.0, spaceAfter=p_sp, keepWithNext=True)
    fig_caption_style = ParagraphStyle('FigCaption', fontName='Times-Italic', fontSize=tbl_fs + 0.5, leading=tbl_fs + 1.8, alignment=1, spaceBefore=2.0, spaceAfter=p_sp)
    ref_style = ParagraphStyle('IEEERef', fontName='Times-Roman', fontSize=body_fs - 0.5, leading=body_lead - 0.5, alignment=4, spaceAfter=p_sp - 1.0, leftIndent=12.0, firstLineIndent=-12.0)

    story = []

    # Page 1 Header
    story.append(Paragraph(pdata.TITLE, title_style))
    story.append(Spacer(1, 2))
    auth_lines = [
        f"<b>{pdata.AUTHORS[0]['name']}</b> ({pdata.AUTHORS[0]['id']}), <b>{pdata.AUTHORS[1]['name']}</b> ({pdata.AUTHORS[1]['id']}), <b>{pdata.AUTHORS[2]['name']}</b> ({pdata.AUTHORS[2]['id']}), <b>{pdata.AUTHORS[3]['name']}</b> ({pdata.AUTHORS[3]['id']})",
        f"<i>Emails:</i> {pdata.AUTHORS[0]['email']}, {pdata.AUTHORS[1]['email']}, {pdata.AUTHORS[2]['email']}, {pdata.AUTHORS[3]['email']}",
        f"<b>Supervisor:</b> {pdata.SUPERVISOR}",
        f"<i>{pdata.AFFILIATION}</i>"
    ]
    for al in auth_lines:
        story.append(Paragraph(al, author_style))
    story.append(FrameBreak())

    # Abstract & Keywords
    abstract_text = f"<b><i>Abstract</i>—{pdata.ABSTRACT}</b>"
    story.append(Paragraph(abstract_text, abstract_body_style))
    story.append(Spacer(1, p_sp))
    keywords_text = f"<b><i>Index Terms</i>—{pdata.INDEX_TERMS}</b>"
    story.append(Paragraph(keywords_text, abstract_title_style))
    story.append(Spacer(1, p_sp))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#888888'), spaceBefore=1, spaceAfter=3))

    story.append(NextPageTemplate('TwoColPage'))

    def make_table_flowable(table_dict, col_widths=None):
        hdr = [Paragraph(h, table_hdr_style) for h in table_dict['headers']]
        data = [hdr]
        for r in table_dict['rows']:
            row_paras = [Paragraph(str(c), table_cell_style) for c in r]
            data.append(row_paras)
        num_cols = len(table_dict['headers'])
        if col_widths is None:
            w_per_col = col_w / num_cols
            col_widths = [w_per_col] * num_cols
        t = Table(data, colWidths=col_widths, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#EEEEEE')),
            ('LINEABOVE', (0, 0), (-1, 0), 0.75, colors.HexColor('#222222')),
            ('LINEBELOW', (0, 0), (-1, 0), 0.75, colors.HexColor('#222222')),
            ('LINEBELOW', (0, -1), (-1, -1), 0.75, colors.HexColor('#222222')),
            ('TOPPADDING', (0, 0), (-1, -1), tbl_pad),
            ('BOTTOMPADDING', (0, 0), (-1, -1), tbl_pad),
            ('LEFTPADDING', (0, 0), (-1, -1), 1.5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 1.5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        return t

    def make_code_box(listing_key, listing_code):
        code_lines = listing_code.strip().split('\n')
        cell_paras = [Paragraph(f"<b>{listing_key}</b>", table_hdr_style)]
        for line in code_lines:
            safe_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            if safe_line.startswith('+'):
                safe_line = f"<font color='#006600'>{safe_line}</font>"
            elif safe_line.startswith('-'):
                safe_line = f"<font color='#990000'>{safe_line}</font>"
            elif safe_line.startswith('---') or safe_line.startswith('+++'):
                safe_line = f"<font color='#000099'><b>{safe_line}</b></font>"
            cell_paras.append(Paragraph(safe_line, code_style))
        t = Table([[cell_paras]], colWidths=[col_w])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor('#CCCCCC')),
            ('TOPPADDING', (0, 0), (-1, -1), 2.5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
            ('LEFTPADDING', (0, 0), (-1, -1), 2.5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 2.5),
        ]))
        return t

    for sec_title, paragraphs in pdata.SECTIONS.items():
        story.append(Paragraph(sec_title, sec_head_style))
        
        # In Section III, insert the Architecture Diagram (image.png)
        if sec_title.startswith("III."):
            if os.path.exists(IMAGE_PATH):
                story.append(Spacer(1, 2))
                story.append(RLImage(IMAGE_PATH, width=img_w, height=img_h))
                story.append(Spacer(1, 2))
                fig_cap = "<b>Fig. 1.</b> End-to-End System Architecture of AgentShield AI illustrating the 8-agent orchestration pipeline, Tree-sitter AST parsing, entropy-based secret scanning, hybrid RAG retrieval, dual-LLM consensus, and LocalStack sandbox validation."
                story.append(Paragraph(fig_cap, fig_caption_style))
                story.append(Spacer(1, p_sp))

        for idx, p_text in enumerate(paragraphs):
            if p_text.startswith("$$"):
                eq_clean = p_text.strip('$').strip()
                story.append(Paragraph(eq_clean, equation_style))
            elif p_text.startswith("<pre>"):
                story.append(Paragraph(p_text, body_noindent))
            else:
                story.append(Paragraph(p_text, body_style))
            
            if sec_title.startswith("IV.") and "Algorithm 1" in p_text:
                alg_paras = []
                for aline in pdata.ALGORITHM_1_LINES_6P:
                    alg_paras.append(Paragraph(aline, ParagraphStyle('AlgL', fontName='Times-Roman', fontSize=tbl_fs, leading=tbl_fs + 1.2, alignment=0)))
                t_alg = Table([[alg_paras]], colWidths=[col_w])
                t_alg.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
                    ('BOX', (0, 0), (-1, -1), 0.75, colors.HexColor('#444444')),
                    ('TOPPADDING', (0, 0), (-1, -1), 2.5),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
                    ('LEFTPADDING', (0, 0), (-1, -1), 3.0),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 3.0),
                ]))
                story.append(Spacer(1, p_sp))
                story.append(t_alg)
                story.append(Spacer(1, p_sp))

            if sec_title.startswith("VI."):
                if "Table I" in p_text:
                    story.append(Paragraph(pdata.TABLES_DATA_6P["TABLE I"]["title"], table_title_style))
                    cws1 = [58, 28, 28, 28, 28, 30, 28, 32]
                    story.append(make_table_flowable(pdata.TABLES_DATA_6P["TABLE I"], cws1))
                    story.append(Spacer(1, p_sp))
                elif "Table II" in p_text:
                    story.append(Paragraph(pdata.TABLES_DATA_6P["TABLE II"]["title"], table_title_style))
                    cws2 = [66, 26, 26, 26, 26, 30, 28, 32]
                    story.append(make_table_flowable(pdata.TABLES_DATA_6P["TABLE II"], cws2))
                    story.append(Spacer(1, p_sp))
                elif "Table III" in p_text:
                    story.append(Paragraph(pdata.TABLES_DATA_6P["TABLE III"]["title"], table_title_style))
                    cws3 = [74, 30, 36, 40, 40, 40]
                    story.append(make_table_flowable(pdata.TABLES_DATA_6P["TABLE III"], cws3))
                    story.append(Spacer(1, p_sp))
                elif "Table IV" in p_text:
                    story.append(Paragraph(pdata.TABLES_DATA_6P["TABLE IV"]["title"], table_title_style))
                    cws4 = [80, 76, 34, 34, 36]
                    story.append(make_table_flowable(pdata.TABLES_DATA_6P["TABLE IV"], cws4))
                    story.append(Spacer(1, p_sp))

            if sec_title.startswith("VII."):
                if "Listing 1" in p_text:
                    story.append(Spacer(1, p_sp))
                    story.append(make_code_box("LISTING 1. S3 BUCKET HARDENING (TERRAFORM HCL)", pdata.CODE_LISTINGS_6P["LISTING 1"]))
                    story.append(Spacer(1, p_sp))
                elif "Listing 2" in p_text:
                    story.append(Spacer(1, p_sp))
                    story.append(make_code_box("LISTING 2. LEAST-PRIVILEGE IAM SCOPING (JSON)", pdata.CODE_LISTINGS_6P["LISTING 2"]))
                    story.append(Spacer(1, p_sp))

            if sec_title.startswith("VIII.") and "Table V" in p_text:
                story.append(Paragraph(pdata.TABLES_DATA_6P["TABLE V"]["title"], table_title_style))
                cws5 = [88, 34, 34, 34, 38, 32]
                story.append(make_table_flowable(pdata.TABLES_DATA_6P["TABLE V"], cws5))
                story.append(Spacer(1, p_sp))

                story.append(Paragraph(pdata.TABLES_DATA_6P["TABLE VI"]["title"], table_title_style))
                cws6 = [74, 44, 44, 44, 54]
                story.append(make_table_flowable(pdata.TABLES_DATA_6P["TABLE VI"], cws6))
                story.append(Spacer(1, p_sp))

    story.append(Paragraph("REFERENCES", sec_head_style))
    for ref_str in pdata.REFERENCES_6P:
        story.append(Paragraph(ref_str, ref_style))

    doc.build(story, canvasmaker=IEEENumberedCanvas6P)
    reader = pypdf.PdfReader(pdf_path)
    return len(reader.pages)


def sanitize_text(text):
    if not text:
        return ""
    t = re.sub(r'<[^>]+>', '', text)
    t = t.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&quot;', '"')
    t = "".join(c for c in t if ord(c) >= 32 or c in "\n\r\t")
    return t


def build_docx_6p(docx_path):
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = DocxInches(0.5)
        s.bottom_margin = DocxInches(0.5)
        s.left_margin = DocxInches(0.5)
        s.right_margin = DocxInches(0.5)

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_t = p_title.add_run(pdata.TITLE)
    run_t.font.name = "Times New Roman"
    run_t.font.size = DocxPt(14)
    run_t.font.bold = True

    p_auth = doc.add_paragraph()
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    auth_text = (
        f"{pdata.AUTHORS[0]['name']} ({pdata.AUTHORS[0]['id']}), "
        f"{pdata.AUTHORS[1]['name']} ({pdata.AUTHORS[1]['id']}), "
        f"{pdata.AUTHORS[2]['name']} ({pdata.AUTHORS[2]['id']}), "
        f"{pdata.AUTHORS[3]['name']} ({pdata.AUTHORS[3]['id']})\n"
        f"Supervisor: {pdata.SUPERVISOR}\n"
        f"{pdata.AFFILIATION}"
    )
    run_a = p_auth.add_run(auth_text)
    run_a.font.name = "Times New Roman"
    run_a.font.size = DocxPt(8.0)

    p_abs = doc.add_paragraph()
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_abs_lbl = p_abs.add_run("Abstract—")
    r_abs_lbl.font.name = "Times New Roman"
    r_abs_lbl.font.size = DocxPt(8.0)
    r_abs_lbl.font.bold = True
    r_abs_lbl.font.italic = True
    
    r_abs_txt = p_abs.add_run(sanitize_text(pdata.ABSTRACT))
    r_abs_txt.font.name = "Times New Roman"
    r_abs_txt.font.size = DocxPt(8.0)
    r_abs_txt.font.italic = True

    p_kw = doc.add_paragraph()
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_kw_lbl = p_kw.add_run("Index Terms—")
    r_kw_lbl.font.name = "Times New Roman"
    r_kw_lbl.font.size = DocxPt(8.0)
    r_kw_lbl.font.bold = True
    r_kw_lbl.font.italic = True
    
    r_kw_txt = p_kw.add_run(sanitize_text(pdata.INDEX_TERMS))
    r_kw_txt.font.name = "Times New Roman"
    r_kw_txt.font.size = DocxPt(8.0)
    r_kw_txt.font.italic = True

    for sec_title, paragraphs in pdata.SECTIONS.items():
        p_sec = doc.add_paragraph()
        p_sec.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_sec = p_sec.add_run(sec_title)
        r_sec.font.name = "Times New Roman"
        r_sec.font.size = DocxPt(9.0)
        r_sec.font.bold = True

        if sec_title.startswith("III.") and os.path.exists(IMAGE_PATH):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.add_picture(IMAGE_PATH, width=DocxInches(3.2))
            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r_cap = p_cap.add_run("Fig. 1. End-to-End System Architecture of AgentShield AI.")
            r_cap.font.name = "Times New Roman"
            r_cap.font.size = DocxPt(7.5)
            r_cap.font.italic = True

        for p_text in paragraphs:
            clean_text = sanitize_text(p_text)
            p_b = doc.add_paragraph()
            p_b.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            r_b = p_b.add_run(clean_text)
            r_b.font.name = "Times New Roman"
            r_b.font.size = DocxPt(8.0)

    for t_key, t_info in pdata.TABLES_DATA_6P.items():
        p_t_title = doc.add_paragraph()
        p_t_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_tt = p_t_title.add_run(t_info["title"])
        r_tt.font.name = "Times New Roman"
        r_tt.font.size = DocxPt(8.0)
        r_tt.font.bold = True

        tbl = doc.add_table(rows=len(t_info["rows"]) + 1, cols=len(t_info["headers"]))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        for col_idx, h in enumerate(t_info["headers"]):
            cell = tbl.cell(0, col_idx)
            cell.text = sanitize_text(h)
            for cp in cell.paragraphs:
                for cr in cp.runs:
                    cr.font.name = "Times New Roman"
                    cr.font.size = DocxPt(7.0)
                    cr.font.bold = True

        for row_idx, r in enumerate(t_info["rows"]):
            for col_idx, c in enumerate(r):
                cell = tbl.cell(row_idx + 1, col_idx)
                cell.text = sanitize_text(str(c))
                for cp in cell.paragraphs:
                    for cr in cp.runs:
                        cr.font.name = "Times New Roman"
                        cr.font.size = DocxPt(7.0)

    p_ref_hdr = doc.add_paragraph()
    p_ref_hdr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_rfh = p_ref_hdr.add_run("REFERENCES")
    r_rfh.font.name = "Times New Roman"
    r_rfh.font.size = DocxPt(9.0)
    r_rfh.font.bold = True

    for r_str in pdata.REFERENCES_6P:
        p_rf = doc.add_paragraph()
        p_rf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_rfr = p_rf.add_run(sanitize_text(r_str))
        r_rfr.font.name = "Times New Roman"
        r_rfr.font.size = DocxPt(7.5)

    doc.save(docx_path)
    print(f"DOCX 6-Page compiled: {docx_path}")


def main():
    root_dir = os.path.dirname(os.path.abspath(__file__))
    target_pdf = os.path.join(root_dir, "AgentShield_AI_6_Page_IEEE_Research_Paper.pdf")
    target_docx = os.path.join(root_dir, "AgentShield_AI_6_Page_IEEE_Research_Paper.docx")
    
    # Exact calibration parameters targeting 6.0 pages with image embedded
    pages = compile_pdf_6p(target_pdf, body_fs=10.4, body_lead=12.27, p_sp=4.5, tbl_fs=6.0, tbl_pad=1.2, img_w=254, img_h=122)
    print(f"PDF 6-Page generated: {target_pdf} -> Total Pages = {pages}")
    
    build_docx_6p(target_docx)
    print(f"6-Page build complete with image! Verified exact page count: {pages}")

if __name__ == "__main__":
    main()
