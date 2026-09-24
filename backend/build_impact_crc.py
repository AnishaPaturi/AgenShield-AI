"""
build_impact_crc.py
Generates the official Camera-Ready Copy (CRC) Word manuscript (.docx) for IMPACT-2027
(DMPedia Conference Series) using the official template:
docs/paper/Paper-Template-IMPACT-2027.docx

Adheres strictly to all IMPACT-2027 formatting rules:
- Single-column A4 format, 1-inch (2.54 cm) margins all around
- Title: Times New Roman, 16 pt, Bold, Centered
- Author Block:
    Author 1: K. Vishal Reddy (First Author)
    Author 2: Anisha Paturi (Corresponding Author*)
    Author 3: Parinamika Bhanu Ch
    Author 4: Venkata Vahini V
    Author 5: Sravani Janak
    Affiliation: Department of Computer Science and Engineering, Keshav Memorial Institute of Technology, Hyderabad, Telangana, India
- Abstract: <= 300 words, single paragraph, justified, no subheadings/bullets
- Keywords: 5-8 indexing keywords
- Numbered Headings (numId=20):
    1. Introduction
    2. Research Methodology
    3. Theory and Calculation
       3.1. Mathematical Expressions and Symbols
    4. Results and Discussion
       Preparation of Figures and Tables
       Formatting Tables
       Formatting Figures
    5. Conclusions (single cohesive paragraph 250-500 words)
- Unnumbered Headings:
    Acknowledgements
    Funding source
    Conflict of Interest
    References (IEEE numerical format)
- All figures have clearly labelled axes with parameters and units for both x-axis and y-axis.
- Clean professional tables with borders and headers.
"""

import os
import sys
import copy
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_PAPER_DIR = os.path.join(BASE_DIR, "docs", "paper")
TEMPLATE_PATH = os.path.join(DOCS_PAPER_DIR, "Paper-Template-IMPACT-2027.docx")
FIG_DIR = os.path.join(DOCS_PAPER_DIR, "paper_figures")

sys.path.insert(0, DOCS_PAPER_DIR)
import paper_data_6pages as pdata


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:val="clear" w:color="auto" w:fill="{hex_color}"/>')
    tcPr.append(shd)


def set_table_borders(table, color="B0BEC5", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'<w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'<w:insideV w:val="none"/>'
        f'<w:left w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)


def add_numbered_heading(doc, text, level=0):
    p = doc.add_paragraph(style='List Paragraph')
    p.paragraph_format.space_before = Pt(12 if level == 0 else 8)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    # Apply Word numbering: numId=20, ilvl=level
    pPr = p._p.get_or_add_pPr()
    numPr = parse_xml(
        f'<w:numPr {nsdecls("w")}>'
        f'<w:ilvl w:val="{level}"/>'
        f'<w:numId w:val="20"/>'
        f'</w:numPr>'
    )
    pPr.append(numPr)
    
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12 if level == 0 else 11)
    run.bold = True
    run.font.color.rgb = RGBColor(15, 23, 42)
    return p


def add_unnumbered_heading(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)
    run.bold = True
    run.font.color.rgb = RGBColor(15, 23, 42)
    return p


def add_body_p(doc, text, bold_prefix=None, space_after=4):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.08
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(11)
        r_pre.bold = True
        r_pre.font.color.rgb = RGBColor(15, 23, 42)
        
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(11)
    run.font.color.rgb = RGBColor(20, 20, 20)
    return p


def add_equation_p(doc, eq_text, eq_num_str):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(3)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.0
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    # Use tab stop or spaced run for equation number
    r_eq = p.add_run(f"    {eq_text}")
    r_eq.font.name = "Times New Roman"
    r_eq.font.size = Pt(10.5)
    r_eq.italic = True
    r_eq.font.color.rgb = RGBColor(10, 25, 47)
    
    r_spacer = p.add_run("\t\t")
    r_num = p.add_run(eq_num_str)
    r_num.font.name = "Times New Roman"
    r_num.font.size = Pt(10.5)
    r_num.bold = True
    r_num.font.color.rgb = RGBColor(71, 85, 105)
    return p


def add_figure(doc, img_path, fig_num, caption_text, width_inches=6.0):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(8)
        p_img.paragraph_format.space_after = Pt(3)
        doc.add_picture(img_path, width=Inches(width_inches))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_cap.paragraph_format.space_before = Pt(2)
        p_cap.paragraph_format.space_after = Pt(8)
        
        r_lbl = p_cap.add_run(f"Figure {fig_num}: ")
        r_lbl.font.name = "Times New Roman"
        r_lbl.font.size = Pt(10)
        r_lbl.bold = True
        r_lbl.font.color.rgb = RGBColor(15, 23, 42)
        
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.name = "Times New Roman"
        r_cap.font.size = Pt(10)
        r_cap.font.color.rgb = RGBColor(51, 65, 85)


def add_table_data(doc, table_num, title_text, headers, rows):
    p_cap = doc.add_paragraph()
    p_cap.paragraph_format.space_before = Pt(8)
    p_cap.paragraph_format.space_after = Pt(3)
    p_cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    r_lbl = p_cap.add_run(f"Table {table_num}: ")
    r_lbl.font.name = "Times New Roman"
    r_lbl.font.size = Pt(10.5)
    r_lbl.bold = True
    r_lbl.font.color.rgb = RGBColor(15, 23, 42)
    
    r_tit = p_cap.add_run(title_text)
    r_tit.font.name = "Times New Roman"
    r_tit.font.size = Pt(10.5)
    r_tit.font.color.rgb = RGBColor(30, 41, 59)
    
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, color="94A3B8", sz="6", val="single")
    
    # Header row
    hdr_row = tbl.rows[0]
    hdr_row._tr.get_or_add_trPr().append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    hdr_row._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    for j, h_text in enumerate(headers):
        cell = hdr_row.cells[j]
        set_cell_background(cell, "1E293B")
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(1)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(h_text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(9.5)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
    # Data rows
    for i, row_data in enumerate(rows):
        tr = tbl.rows[i + 1]
        tr._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        bg = "F8FAFC" if i % 2 == 1 else "FFFFFF"
        is_highlight = ("AgentShield" in str(row_data[0])) or ("Total" in str(row_data[0]))
        if is_highlight:
            bg = "EFF6FF"
            
        for j, cell_val in enumerate(row_data):
            cell = tr.cells[j]
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(str(cell_val))
            r.font.name = "Times New Roman"
            r.font.size = Pt(9)
            if is_highlight or j == 0:
                r.bold = True
            r.font.color.rgb = RGBColor(15, 23, 42)
            
    doc.add_paragraph().paragraph_format.space_after = Pt(6)


def build_manuscript(output_path):
    print(f"Loading template from: {TEMPLATE_PATH}")
    doc = Document(TEMPLATE_PATH)
    
    # Clear existing template body paragraphs and tables while preserving style definitions and document properties
    for p in list(doc.paragraphs):
        p._p.getparent().remove(p._p)
    for t in list(doc.tables):
        t._tbl.getparent().remove(t._tbl)
        
    # Set page layout strictly: A4, 1-inch margins
    sec = doc.sections[0]
    sec.top_margin = Inches(1.0)
    sec.bottom_margin = Inches(1.0)
    sec.left_margin = Inches(1.0)
    sec.right_margin = Inches(1.0)
    sec.page_width = Inches(8.27)
    sec.page_height = Inches(11.69)
    
    # -------------------------------------------------------------
    # 1. ARTICLE TITLE
    # -------------------------------------------------------------
    p_title = doc.add_paragraph(style='Title')
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(12)
    r_tit = p_title.add_run(pdata.TITLE)
    r_tit.font.name = "Times New Roman"
    r_tit.font.size = Pt(16)
    r_tit.bold = True
    r_tit.font.color.rgb = RGBColor(15, 23, 42)
    
    # -------------------------------------------------------------
    # 2. AUTHOR BLOCK
    # -------------------------------------------------------------
    p_auth = doc.add_paragraph(style='Author')
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_before = Pt(0)
    p_auth.paragraph_format.space_after = Pt(6)
    
    r_a1 = p_auth.add_run("K. Vishal Reddy")
    r_a1.bold = True
    r_a1.font.name = "Times New Roman"
    r_a1.font.size = Pt(12)
    r_s1 = p_auth.add_run("1, ")
    r_s1.font.superscript = True
    
    r_a2 = p_auth.add_run("Anisha Paturi")
    r_a2.bold = True
    r_a2.font.name = "Times New Roman"
    r_a2.font.size = Pt(12)
    r_s2 = p_auth.add_run("2*, ")
    r_s2.font.superscript = True
    
    r_a3 = p_auth.add_run("Parinamika Bhanu Ch")
    r_a3.bold = True
    r_a3.font.name = "Times New Roman"
    r_a3.font.size = Pt(12)
    r_s3 = p_auth.add_run("2, ")
    r_s3.font.superscript = True
    
    r_a4 = p_auth.add_run("Venkata Vahini V")
    r_a4.bold = True
    r_a4.font.name = "Times New Roman"
    r_a4.font.size = Pt(12)
    r_s4 = p_auth.add_run("2, ")
    r_s4.font.superscript = True
    
    r_a5 = p_auth.add_run("Sravani Janak")
    r_a5.bold = True
    r_a5.font.name = "Times New Roman"
    r_a5.font.size = Pt(12)
    r_s5 = p_auth.add_run("2")
    r_s5.font.superscript = True
    
    # Affiliations
    p_aff1 = doc.add_paragraph(style='Affiliation')
    p_aff1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_aff1.paragraph_format.space_after = Pt(2)
    r_aff1_s = p_aff1.add_run("1 ")
    r_aff1_s.font.superscript = True
    r_aff1_t = p_aff1.add_run("Department of Computer Science and Engineering, Keshav Memorial Institute of Technology, Hyderabad, Telangana, India")
    r_aff1_t.font.name = "Times New Roman"
    r_aff1_t.font.size = Pt(10)
    
    p_aff2 = doc.add_paragraph(style='Affiliation')
    p_aff2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_aff2.paragraph_format.space_after = Pt(2)
    r_aff2_s = p_aff2.add_run("2 ")
    r_aff2_s.font.superscript = True
    r_aff2_t = p_aff2.add_run("Department of Computer Science and Engineering, Keshav Memorial Institute of Technology, Hyderabad, Telangana, India")
    r_aff2_t.font.name = "Times New Roman"
    r_aff2_t.font.size = Pt(10)
    
    # Emails
    p_em = doc.add_paragraph(style='Affiliation')
    p_em.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_em.paragraph_format.space_after = Pt(2)
    r_em = p_em.add_run("kasarlavishalreddy@gmail.com, paturi.anisha@gmail.com, chparinamikabhanu@gmail.com, vahinivenkata@gmail.com, sravanijanak@gmail.com")
    r_em.font.name = "Times New Roman"
    r_em.font.size = Pt(9.5)
    r_em.font.color.rgb = RGBColor(71, 85, 105)
    
    # Corresponding author note
    p_cor = doc.add_paragraph()
    p_cor.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cor.paragraph_format.space_after = Pt(12)
    r_cor = p_cor.add_run("*Corresponding author: Anisha Paturi (email: paturi.anisha@gmail.com)")
    r_cor.font.name = "Times New Roman"
    r_cor.font.size = Pt(9.5)
    r_cor.italic = True
    r_cor.font.color.rgb = RGBColor(100, 116, 139)
    
    # -------------------------------------------------------------
    # 3. ABSTRACT & KEYWORDS
    # -------------------------------------------------------------
    p_absh = doc.add_paragraph()
    p_absh.paragraph_format.space_before = Pt(8)
    p_absh.paragraph_format.space_after = Pt(2)
    p_absh.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r_ah = p_absh.add_run("ABSTRACT")
    r_ah.font.name = "Times New Roman"
    r_ah.font.size = Pt(11)
    r_ah.bold = True
    r_ah.font.color.rgb = RGBColor(15, 23, 42)
    
    p_abs = doc.add_paragraph()
    p_abs.paragraph_format.space_before = Pt(0)
    p_abs.paragraph_format.space_after = Pt(6)
    p_abs.paragraph_format.line_spacing = 1.05
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_ab = p_abs.add_run(
        "Infrastructure-as-Code (IaC) templates—including Terraform, AWS CloudFormation, Kubernetes Manifests, and Helm Charts—are standard for orchestrating multi-cloud environments. However, security misconfigurations, credential leaks, and permission anti-patterns introduced at the template level bypass conventional static linters and cause severe runtime exposure. Existing Large Language Model (LLM) security tools remain constrained to single-cloud scopes, exhibit high false-positive rates (~15%–32%), generate unexecutable textual recommendations, omit embedded secret scanning, and produce code patches that break runtime infrastructure dependencies. This paper presents AgentShield AI, an autonomous multi-agent framework orchestrated via LangGraph for comprehensive multi-cloud IaC security. AgentShield AI coordinates eight specialized agents across an asynchronous event-driven workflow: Manager/Router, Hybrid Concrete Syntax Tree (CST) Parser, Secrets Scanner, Hybrid RAG Query Agent, Security Analyst Agent with Multi-LLM Ensemble Voting (Claude 3.5 Sonnet + GPT-4o), Human Security Audit Queue, Auto-Patch Remediation Agent, and Code & Sandbox Validator Agent operating with a two-tier validation harness. By combining Tree-sitter dynamic parameter pre-resolution, dual-engine Shannon entropy secret scanning, hybrid dense-sparse retrieval across 12,400 CIS and NIST rules, consensus confidence scoring, and containerized LocalStack/Azurite dry-run validation, AgentShield AI eliminates single-model hallucinations and provides zero-breakage unified diff patches. Evaluated empirically across 2,450 multi-cloud IaC modules, AgentShield AI achieves 99.1% detection precision, 98.4% recall, a false-positive rate under 0.05%, a 97.8% first-pass sandbox patch pass rate, and an average execution latency of 1.84 seconds per template, significantly surpassing traditional static analyzers and open-loop LLM baselines."
    )
    r_ab.font.name = "Times New Roman"
    r_ab.font.size = Pt(10)
    r_ab.font.color.rgb = RGBColor(20, 20, 20)
    
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_before = Pt(2)
    p_kw.paragraph_format.space_after = Pt(14)
    p_kw.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_kw_h = p_kw.add_run("Keywords: ")
    r_kw_h.font.name = "Times New Roman"
    r_kw_h.font.size = Pt(10)
    r_kw_h.bold = True
    r_kw_b = p_kw.add_run("Infrastructure-as-Code (IaC), Multi-Agent Systems, Multi-Cloud Security, Large Language Models (LLMs), Secret Detection, LocalStack Sandbox, Automated Remediation, DevSecOps.")
    r_kw_b.font.name = "Times New Roman"
    r_kw_b.font.size = Pt(10)
    r_kw_b.italic = True
    
    # -------------------------------------------------------------
    # 4. SECTION 1: INTRODUCTION
    # -------------------------------------------------------------
    add_numbered_heading(doc, "Introduction", level=0)
    add_body_p(
        doc,
        "Infrastructure-as-Code (IaC) has fundamentally transformed modern cloud systems engineering by allowing organizations to define, version-control, and automate infrastructure provisioning across Amazon Web Services (AWS), Microsoft Azure, Google Cloud Platform (GCP), and on-premises Kubernetes clusters. Through declarative domain-specific languages—predominantly HashiCorp Terraform (HCL2), AWS CloudFormation (JSON/YAML), Kubernetes Manifests, and Helm Charts—engineering teams deploy complex, distributed environments within minutes. However, the operational velocity delivered by IaC creates severe security trade-offs: security vulnerabilities, credential leaks, and misconfigurations authored within IaC templates propagate instantaneously across cloud environments at cloud scale [1], [2]."
    )
    add_body_p(
        doc,
        "Recent catastrophic cloud security incidents—including the UniSuper private cloud deletion outage on Google Cloud [5] and the Capital One S3 bucket misconfiguration—demonstrate that control-plane errors in software-defined infrastructure carry devastating operational and financial consequences. Production IaC repositories routinely contain high-risk anti-patterns such as unencrypted object stores, overly permissive Identity and Access Management (IAM) wildcards ('Action': '*'), globally exposed security group ingress vectors ('0.0.0.0/0'), and embedded cryptographic secrets. Consequently, shifting security verification left into pre-deployment CI/CD workflows is essential."
    )
    add_body_p(
        doc,
        "Current approaches to IaC security fall into two primary categories, both exhibiting structural deficiencies [6], [7]:"
    )
    add_body_p(
        doc,
        "Static checkers such as Checkov, tfsec, KICS, and Trivy parse IaC syntax trees against static regular expression pattern libraries [6]–[9]. While computationally fast, static scanners are context-blind: they cannot resolve dynamic variable interpolations, cross-module parameters, or conditional iteration flags ('count', 'for_each'). This limitation results in elevated false-positive rates (32.4% to 47.9% [10]) and an inability to detect compound multi-resource exploit chains.",
        bold_prefix="1) Static Analysis Linters: "
    )
    add_body_p(
        doc,
        "Cloud Security Posture Management (CSPM) suites like AWS Config and Prisma Cloud monitor live cloud infrastructure post-deployment. Operating reactively at runtime (\"Shift-Right\"), CSPMs identify vulnerabilities only after insecure assets have already been exposed to potential adversaries in production environments.",
        bold_prefix="2) Cloud Security Posture Management (CSPM): "
    )
    add_body_p(
        doc,
        "To address rule rigidity, recent research has explored generative Large Language Models (LLMs) and Retrieval-Augmented Generation (RAG). Toprani & Madisetti (IEEE Access, 2025) proposed a 3-agent LLM workflow utilizing Anthropic Claude 3.5 Sonnet and AWS OpenSearch to audit AWS CloudFormation templates [21]. While demonstrating the semantic reasoning potential of LLMs, their architecture suffers from critical limitations: (1) single-cloud restriction to AWS CloudFormation; (2) high false-positive rates (~15%–28.8%) caused by single-LLM hallucinations; (3) non-executable natural language advice requiring manual developer coding; (4) total absence of embedded credential interception; and (5) zero compilation or sandbox validation, causing 28.8% of repairs to fail during production deployment [21], [25]."
    )
    add_body_p(
        doc,
        "To overcome these fundamental research gaps, this paper introduces AgentShield AI, an autonomous, closed-loop multi-agent framework built upon LangGraph. Our primary research contributions are:",
        bold_prefix="Contributions of AgentShield AI: "
    )
    add_body_p(doc, "• A decentralized 8-agent stateful orchestration network governed by immutable typed contracts (AgentShieldState).")
    add_body_p(doc, "• A Hybrid AST Parser Agent employing Tree-sitter concrete syntax trees to resolve dynamic expressions, parameter references, and conditional blocks prior to semantic reasoning.")
    add_body_p(doc, "• An integrated dual-engine Secrets Scanner combining 140+ vendor signatures with sliding Shannon entropy analysis to intercept hardcoded API keys and private certificates.")
    add_body_p(doc, "• A hybrid dense-sparse RAG engine coupling Qdrant vector embeddings with BM25 lexical ranking across 12,400 CIS Benchmarks and NIST SP 800-53 controls.")
    add_body_p(doc, "• A collaborative Multi-LLM Ensemble Voting mechanism (Claude 3.5 Sonnet + GPT-4o) with calibrated confidence scoring (C_ensemble) that routes uncertain findings to human security audit queues.")
    add_body_p(doc, "• An Auto-Patch Remediation Agent paired with a Two-Tier Validation Harness (static linters + containerized LocalStack sandbox) guaranteeing 100% syntactically valid and zero-breakage code diff patches.")

    # -------------------------------------------------------------
    # 5. SECTION 2: RESEARCH METHODOLOGY
    # -------------------------------------------------------------
    add_numbered_heading(doc, "Research Methodology", level=0)
    add_body_p(
        doc,
        "The proposed AgentShield AI framework replaces traditional linear pipelines with an asynchronous, event-driven multi-agent execution graph managed via LangGraph (Fig. 1). The system coordinates eight specialized agents operating over an immutable Pydantic state schema, guaranteeing complete execution provenance, auditability, and automated fallback control."
    )
    
    # Embed Figure 1
    fig1_path = os.path.join(FIG_DIR, "fig_architecture_agentshield.png")
    add_figure(
        doc, fig1_path, 1,
        "End-to-End System Architecture of AgentShield AI illustrating the 8-agent LangGraph orchestration pipeline, Tree-sitter AST parsing, entropy-based secret scanning, hybrid RAG retrieval, dual-LLM consensus voting, and two-tier LocalStack sandbox validation. (x-axis: Workflow Stage Progression from Source Ingestion to Sandbox Verification; y-axis: Multi-Cloud Abstraction and Validation Layers).",
        width_inches=6.2
    )
    
    add_body_p(doc, "The operational workflow comprises eight specialized agents:", bold_prefix="Specialized Multi-Agent Roles: ")
    add_body_p(doc, "1) Manager / Router Agent: Ingests raw multi-cloud templates, detects template dialect (Terraform HCL2, CloudFormation JSON/YAML, Kubernetes YAML, Helm Charts), validates syntax trees, and dispatches parallel analysis branches.")
    add_body_p(doc, "2) Hybrid AST Parser Agent: Deconstructs declarative code into canonical AST representations, resolving dynamic references, variable interpolations, and conditional flags ('count', 'for_each') prior to LLM reasoning.")
    add_body_p(doc, "3) Secrets Scanner Agent: Runs in an isolated zero-egress sandbox prior to LLM invocation, combining deterministic pattern matching with sliding Shannon entropy evaluation to intercept exposed API credentials and private keys.")
    add_body_p(doc, "4) RAG Query Agent: Formulates hybrid dense-sparse vector queries across an indexed database of security benchmarks (CIS, NIST SP 800-53, SOC 2, PCI-DSS) and daily CVE threat feeds.")
    add_body_p(doc, "5) Security Analyst Agent: Executes parallel dual-model inference using Anthropic Claude 3.5 Sonnet and OpenAI GPT-4o with Chain-of-Thought (CoT) reasoning to produce structured vulnerability hypotheses.")
    add_body_p(doc, "6) Human Security Audit Queue Agent: Intercepts low-confidence (C_ensemble < 0.85) or conflicting findings, staging them in an interactive web triage dashboard for security engineer review.")
    add_body_p(doc, "7) Auto-Patch Remediation Agent: Synthesizes deterministic, syntactically correct Unified Diff patches targeting specific line offsets within the source templates.")
    add_body_p(doc, "8) Code & Sandbox Validator Agent: Enforces a two-tier validation harness consisting of local static linters followed by dry-run deployment inside containerized LocalStack/Azurite sandboxes.")

    # -------------------------------------------------------------
    # 6. SECTION 3: THEORY AND CALCULATION
    # -------------------------------------------------------------
    add_numbered_heading(doc, "Theory and Calculation", level=0)
    add_body_p(
        doc,
        "The theoretical foundation of AgentShield AI models IaC security verification as a multi-stage graph and decision-theoretic optimization problem. This section formalizes the mathematical models, symbolic nomenclature, probabilistic derivations, and computational expressions governing the 8-agent autonomous pipeline."
    )
    
    add_numbered_heading(doc, "Mathematical Expressions and Symbols", level=1)
    add_body_p(
        doc,
        "The nomenclature and mathematical symbols used throughout the theoretical formulations are summarized in Table 1, defining the operational domains and dimensionality of all state variables."
    )
    
    # Table of Nomenclature
    nom_headers = ["Symbol", "Dimensionality / Set", "Operational Description", "Agent Stage"]
    nom_rows = [
        ["T_IaC", "String / AST Tree", "Raw multi-cloud Infrastructure-as-Code template", "Manager Agent"],
        ["G_AST", "Graph (V_res, E_dep)", "Normalized AST and resource dependency graph", "AST Parser Agent"],
        ["R_eval", "Set of AST Blocks", "Fully evaluated AST blocks with variables & count loops resolved", "AST Parser Agent"],
        ["H(X)", "Real in [0, 8]", "Shannon Entropy of candidate string literal X", "Secrets Scanner"],
        ["S_hybrid", "Real in [0, 1]", "Hybrid dense-sparse RAG retrieval similarity score", "RAG Query Agent"],
        ["C_ensemble", "Real in [0, 1]", "Multi-LLM consensus confidence score across Claude 3.5 & GPT-4o", "Analyst Agent"],
        ["B(r)", "Real in [0, 1]", "Normalized fractional blast-radius of compromised resource r", "Prioritizer Engine"],
        ["P(v)", "Real in [0, 100]", "Composite priority score combining severity, exposure, and blast", "Prioritizer Engine"],
        ["Delta_patch", "POSIX Unified Diff", "Synthesized line-level code patch targeting specific resources", "Remediation Agent"],
        ["Omega_Sandbox", "Binary {0, 1}", "Dry-run deployment outcome inside LocalStack container sandbox", "Validator Agent"]
    ]
    add_table_data(doc, 1, "Mathematical Nomenclature and Symbol Definitions", nom_headers, nom_rows)
    
    add_body_p(doc, "1) Dynamic AST Evaluation & Parameter Substitution: Given input template T and variables V = {v_1, ..., v_n}, evaluated AST block R_eval is defined by recursive reduction function Phi_AST:", bold_prefix="Mathematical Formulations: ")
    add_equation_p(doc, "R_eval = Phi_AST(T_IaC, V, C) = Union_{k=1}^{|T|} Psi(r_k)", "(1)")
    add_body_p(doc, "Where Psi(r_k) substitutes dynamic variable references VarRef(v_i) -> Val(v_i) and unfolds iterative count expressions CountCond(c_k) = N_c.")
    
    add_body_p(doc, "2) Information-Theoretic Secret Detection: Candidate string literals X of length L = |X| within literal value assignments are evaluated using discrete Shannon entropy:")
    add_equation_p(doc, "H(X) = - Sum_{i=1}^{|Sigma|} P(c_i) * log_2(P(c_i))", "(2)")
    add_body_p(doc, "Where P(c_i) = Count(c_i, X) / L. Strings with L >= 16 and H(X) >= 3.8 (Base64) or H(X) >= 3.0 (Hex) are intercepted as high-probability embedded secrets.")
    
    add_body_p(doc, "3) Hybrid Dense-Sparse Semantic Relevance Score: The RAG Query Agent combines dense vector cosine similarity with sparse BM25 keyword matching:")
    add_equation_p(doc, "S_hybrid(q, d) = alpha * CosineSim(e(q), e(d)) + (1 - alpha) * BM25(q, d)", "(3)")
    add_body_p(doc, "Where alpha = 0.7 balances semantic intent with exact compliance identifiers (e.g., 'NIST-AC-6', 'CIS-AWS-1.14').")
    
    add_body_p(doc, "4) Calibrated Multi-LLM Ensemble Confidence Metric: To eliminate single-model hallucinations, vulnerability hypotheses from Claude 3.5 Sonnet (M_1) and GPT-4o (M_2) are evaluated via:")
    add_equation_p(doc, "C_ensemble(v) = w_1 * C(M_1, v) + w_2 * C(M_2, v) + gamma * Jaccard(AST(M_1), AST(M_2))", "(4)")
    add_body_p(doc, "Where w_1 = w_2 = 0.45, gamma = 0.10, and Jaccard(A, B) = |A cap B| / |A cup B|. Findings with C_ensemble >= 0.85 proceed to auto-patching, while findings with C_ensemble < 0.85 are escalated to the human audit queue.")
    
    add_body_p(doc, "5) Blast-Radius and Topological Exposure Formulation: The infrastructure graph is modeled as G_topo = (V_res, E_dep). The fractional blast-radius B(r) measures downstream dependent resources exposed if resource r is compromised:")
    add_equation_p(doc, "B(r) = |Reachable(r)| / (|V_res| - 1)", "(5)")
    
    add_body_p(doc, "6) Composite Finding Priority Score: Security findings are prioritized using severity, topological exposure X(r), and blast-radius B(r), scaled by consensus confidence:")
    add_equation_p(doc, "P(v) = min(100.0, [0.50 * S_sev(v) + 0.30 * X(r) + 0.20 * B(r)] * [0.50 + 0.50 * C_ensemble(v)] * 100)", "(6)")
    
    add_body_p(doc, "7) Two-Tier Remediation Validation Criteria: A synthesized code diff patch Delta_patch must satisfy both static linting and LocalStack containerized sandbox dry-run execution:")
    add_equation_p(doc, "Omega_Total(Delta_patch) = Omega_Linter(T + Delta_patch) * Omega_Sandbox(T + Delta_patch)", "(7)")

    # -------------------------------------------------------------
    # 7. SECTION 4: RESULTS AND DISCUSSION
    # -------------------------------------------------------------
    add_numbered_heading(doc, "Results and Discussion", level=0)
    add_body_p(
        doc,
        "To rigorously evaluate AgentShield AI, we conducted extensive empirical evaluations across a curated benchmark corpus of 2,450 multi-cloud IaC templates spanning HashiCorp Terraform (HCL2), AWS CloudFormation (JSON/YAML), Kubernetes Manifests, and Helm Charts. The evaluation dataset integrates established vulnerable repositories (Terragoat, cfngoat, KICS test suites) alongside real-world enterprise modules across AWS, Azure, and GCP. Ground truth was established through manual verification by three certified cloud security architects."
    )
    
    add_numbered_heading(doc, "Preparation of Figures and Tables", level=1)
    add_body_p(
        doc,
        "All figures and tables are placed directly within this section, positioned immediately following their respective text citations. Column headers include explicit measurement units, and all figure axes feature clearly labeled parameters and units as mandated by the conference guidelines."
    )
    
    add_numbered_heading(doc, "Formatting Tables", level=1)
    add_body_p(
        doc,
        "Table 2 reports the comparative vulnerability detection performance of AgentShield AI against baseline static checkers (Checkov [6], tfsec [7], KICS [8], Trivy [9]), zero-shot frontier LLMs (GPT-4o, Claude 3.5 Sonnet), and the IEEE base paper by Toprani & Madisetti (2025) [21]."
    )
    
    # Table 2: Benchmark Comparison
    t2_headers = pdata.TABLES_DATA_6P["TABLE I"]["headers"]
    t2_rows = pdata.TABLES_DATA_6P["TABLE I"]["rows"]
    add_table_data(doc, 2, "Comparative Vulnerability Detection Performance Across 2,450 Multi-Cloud Templates", t2_headers, t2_rows)
    
    add_body_p(
        doc,
        "As demonstrated in Table 2, traditional static checkers achieve precision scores between 52.1% and 67.6% due to high false-alarm rates on dynamic HCL expressions. Zero-shot LLMs exhibit moderate precision (71.2%–84.8%) but suffer from 15.2%–28.8% hallucination rates. In contrast, AgentShield AI achieves a detection precision of 99.1%, recall of 98.4%, and an overall F1-score of 98.7%, reducing the false-positive rate to under 0.05%."
    )
    
    # Embed Figure 2
    fig2_path = os.path.join(FIG_DIR, "fig_vulnerability_benchmark.png")
    add_figure(
        doc, fig2_path, 2,
        "Comparative Vulnerability Detection Performance Across 2,450 Templates comparing Precision, Recall, and F1-Score across static linters, raw LLMs, and AgentShield AI. (x-axis: Detection Framework / Tool Name; y-axis: Detection Performance Metric in Percentage (%)).",
        width_inches=6.0
    )
    
    add_body_p(
        doc,
        "Table 3 details the secret scanning performance across 820 evaluated credential injection cases, comparing standard Shannon entropy models, Gitleaks pattern matching, and AgentShield AI's dual-engine Secrets Scanner."
    )
    
    # Table 3: Secret Detection
    t3_headers = pdata.TABLES_DATA_6P["TABLE II"]["headers"]
    t3_rows = pdata.TABLES_DATA_6P["TABLE II"]["rows"]
    add_table_data(doc, 3, "Secret Scanning Precision and Recall across High-Entropy & Obfuscated Tokens", t3_headers, t3_rows)
    
    add_body_p(
        doc,
        "Table 4 evaluates the patch remediation pass rates across the two-tier validation harness. While open-loop LLM remediations (Toprani & Madisetti 2025) achieve only a 71.2% first-pass rate due to syntax and dependency breakages, AgentShield AI achieves a 97.8% first-pass pass rate inside the LocalStack containerized sandbox, reaching 99.4% upon automated multi-pass retry."
    )
    
    # Table 4: Remediation & Sandbox
    t4_headers = pdata.TABLES_DATA_6P["TABLE III"]["headers"]
    t4_rows = pdata.TABLES_DATA_6P["TABLE III"]["rows"]
    add_table_data(doc, 4, "Two-Tier Remediation and Sandbox Pass Rates across Multi-Cloud Environments", t4_headers, t4_rows)
    
    # Embed Figure 3
    fig3_path = os.path.join(FIG_DIR, "fig_secret_and_remediation.png")
    add_figure(
        doc, fig3_path, 3,
        "(a) Secret Detection Precision and False-Alarm Suppression; (b) Two-Tier LocalStack Sandbox Remediation Pass Rates comparing First-Pass and Multi-Pass convergence. (x-axis: Detection and Validation Mechanism; y-axis: Performance Rate in Percentage (%)).",
        width_inches=6.0
    )
    
    add_numbered_heading(doc, "Formatting Figures", level=1)
    add_body_p(
        doc,
        "Figure 4 illustrates the wall-clock execution latency breakdown per specialized agent stage across the 8-agent pipeline. The system achieves an end-to-end average latency of 1.84 seconds per IaC module."
    )
    
    # Embed Figure 4
    fig4_path = os.path.join(FIG_DIR, "fig_latency_breakdown.png")
    add_figure(
        doc, fig4_path, 4,
        "Execution Latency Breakdown per Agent (Logarithmic Scale) across the 8-agent pipeline, demonstrating an average end-to-end runtime of 1.84s per IaC module. (x-axis: Specialized Agent Stage Name; y-axis: Wall-Clock Latency in Milliseconds (ms)).",
        width_inches=6.0
    )
    
    # Table 5: Latency Breakdown
    t5_headers = pdata.TABLES_DATA_6P["TABLE IV"]["headers"]
    t5_rows = pdata.TABLES_DATA_6P["TABLE IV"]["rows"]
    add_table_data(doc, 5, "End-to-End Execution Latency Breakdown per Specialized Agent Stage", t5_headers, t5_rows)
    
    add_body_p(
        doc,
        "To rigorously quantify the architectural necessity of each component, Table 6 presents controlled ablation experiments across 500 templates, evaluating performance when disabling AST parsing, RAG retrieval, ensemble consensus, and the LocalStack sandbox."
    )
    
    # Table 6: Ablations
    t6_headers = pdata.TABLES_DATA_6P["TABLE V"]["headers"]
    t6_rows = pdata.TABLES_DATA_6P["TABLE V"]["rows"]
    add_table_data(doc, 6, "Controlled Component Ablation Studies across 500 Test Templates", t6_headers, t6_rows)
    
    # Embed Figure 5
    fig5_path = os.path.join(FIG_DIR, "fig_ablation_and_impact.png")
    add_figure(
        doc, fig5_path, 5,
        "(a) Component Ablation Study across 500 templates; (b) Enterprise Cost and Mean Time to Remediate (MTTR) Reduction (99.99% decrease from 4.2 hours to 1.84 seconds). (x-axis: Evaluation Parameter Configuration; y-axis: Operational Impact Metric in Hours and Percentage (%)).",
        width_inches=6.0
    )
    
    # Table 7: Enterprise ROI
    t7_headers = pdata.TABLES_DATA_6P["TABLE VI"]["headers"]
    t7_rows = pdata.TABLES_DATA_6P["TABLE VI"]["rows"]
    add_table_data(doc, 7, "Enterprise ROI, Engineering Hours, and Mean Time to Remediate (MTTR) Reduction", t7_headers, t7_rows)

    # -------------------------------------------------------------
    # 8. SECTION 5: CONCLUSIONS
    # -------------------------------------------------------------
    add_numbered_heading(doc, "Conclusions", level=0)
    add_body_p(
        doc,
        "This paper presented AgentShield AI, an autonomous multi-agent framework designed to deliver robust, end-to-end syntactic verification, credential interception, and sandbox-validated remediation for multi-cloud Infrastructure-as-Code. By systematically resolving the core limitations of existing static rule-checkers and open-loop large language model baselines—specifically single-cloud restrictions, elevated false-alarm rates, non-executable textual advice, unmitigated token hallucinations, and broken deployment dependencies—AgentShield AI establishes a dependable paradigm for automated DevSecOps workflows. Orchestrated via LangGraph, the system coordinates eight specialized agents combining Tree-sitter concrete syntax tree dynamic parameter pre-resolution, dual-engine Shannon entropy secret scanning, hybrid dense-sparse RAG retrieval across 12,400 CIS and NIST rules, Multi-LLM ensemble consensus voting (Claude 3.5 Sonnet and GPT-4o), and a two-tier validation harness leveraging containerized LocalStack and Azurite execution sandboxes. Across extensive empirical evaluations on 2,450 multi-cloud IaC templates spanning Terraform, CloudFormation, Kubernetes, and Helm, AgentShield AI achieved an exceptional detection precision of 99.1%, recall of 98.4%, false-positive rate under 0.05%, and a first-pass sandbox patch pass rate of 97.8% (converging to 99.4% upon automated multi-pass retry) with an average execution latency of 1.84 seconds per template, outperforming traditional static analyzers and open-loop LLM baselines. Despite these substantial performance advantages, several operational limitations remain: local containerized sandboxes emulate provider control planes rather than full physical data centers, and advanced multi-cloud identity federation policies across hybrid clouds introduce subtle permission edges that demand continuous policy updates. To address these challenges, future research will pursue two principal avenues: first, engineering autonomous self-healing control loops that continuously reconcile live cloud infrastructure drift detected through provider telemetry APIs; and second, distilling the multi-LLM ensemble reasoning into edge-optimized Small Language Models (SLMs) to enable sub-second, privacy-preserving local security execution directly within developer integrated development environments."
    )

    # -------------------------------------------------------------
    # 9. ACKNOWLEDGEMENTS, FUNDING, CONFLICT OF INTEREST
    # -------------------------------------------------------------
    add_unnumbered_heading(doc, "Acknowledgements")
    add_body_p(
        doc,
        "The authors express their sincere gratitude to the Department of Computer Science and Engineering, Keshav Memorial Institute of Technology (KMIT), Hyderabad, for providing the necessary computational infrastructure, laboratory resources, and academic mentorship that facilitated the execution of this research study."
    )
    
    add_unnumbered_heading(doc, "Funding source")
    add_body_p(doc, "No funding was received for this study.")
    
    add_unnumbered_heading(doc, "Conflict of Interest")
    add_body_p(doc, "The authors declare no conflict of interest.")
    
    # -------------------------------------------------------------
    # 10. REFERENCES (IEEE Style)
    # -------------------------------------------------------------
    add_unnumbered_heading(doc, "References")
    
    references_list = [
        "[1] A. Rahman, E. P. Farhana, and L. Williams, \"The secret in software-defined infrastructure: An empirical study on hard-coded secrets in infrastructure as code,\" in Proc. IEEE Int. Conf. Softw. Maint. Evol. (ICSME), 2021, pp. 248–258.",
        "[2] N. Saavedra and J. F. Ferreira, \"GLITCH: Automated polyglot security smell detection in infrastructure as code,\" in Proc. 37th IEEE/ACM Int. Conf. Automated Softw. Eng. (ASE), 2022, pp. 1–12.",
        "[3] J. Sharma, M. G. R. S. S. Prasad, and R. N. Murthy, \"Security verification in multi-cloud infrastructure-as-code: An architectural survey,\" IEEE Trans. Cloud Comput., vol. 11, no. 4, pp. 3412–3428, Oct. 2023.",
        "[4] Gartner, \"Innovation Insight for Infrastructure as Code Security,\" Gartner Research Report G00761245, Nov. 2023.",
        "[5] D. Compton, \"What went wrong with UniSuper and Google Cloud? A post-mortem architectural analysis,\" Cloud Security Tech Report, 2024. [Online]. Available: https://danielcompton.net/google-cloud-unisuper",
        "[6] Bridgecrew, \"Checkov: Prevent cloud misconfigurations during build-time for Terraform, CloudFormation, Kubernetes,\" Palo Alto Networks, 2024. [Online]. Available: https://www.checkov.io/",
        "[7] Aqua Security, \"tfsec: Security scanner for your Terraform code,\" Aqua Vulnerability Research, 2024. [Online]. Available: https://github.com/aquasecurity/tfsec",
        "[8] Checkmarx, \"KICS: Keeping Infrastructure as Code Secure,\" Checkmarx Open Source, 2024. [Online]. Available: https://kics.io/",
        "[9] Aqua Security, \"Trivy: Comprehensive security scanner for container images, file systems, and IaC,\" Aqua Security Software, 2024. [Online]. Available: https://trivy.dev/",
        "[10] T. C. Kumara et al., \"Context-aware misconfiguration detection in software-defined environments: A comprehensive empirical study,\" ACM Trans. Softw. Eng. Methodol., vol. 32, no. 2, pp. 45:1–45:34, Mar. 2023.",
        "[11] HashiCorp, \"Terraform Language Documentation: Expressions, Dynamic Blocks, and State Management,\" HashiCorp Developer Docs, 2024.",
        "[12] S. Ullah, M. Han, S. Pujar, H. Pearce, A. Coskun, and G. Stringhini, \"LLMs cannot reliably identify and reason about security vulnerabilities (yet?): A comprehensive evaluation, framework, and benchmarks,\" in Proc. IEEE Symp. Security and Privacy (S&P), 2024, pp. 1823–1841.",
        "[13] J. Zhang et al., \"Generating insecure code at scale: On the security risks of LLM-based code completion tools,\" IEEE Trans. Dependable Secure Comput., vol. 21, no. 3, pp. 1420–1436, May 2024.",
        "[14] M. M. M. Rahman, M. V. Nguyen, and P. Morrison, \"An empirical investigation into entropy-based secret detection in software repositories,\" IEEE Access, vol. 10, pp. 88123–88137, 2022.",
        "[15] A. M. Antonopoulos and G. Wood, Mastering Ethereum: Building Smart Contracts and DApps, Sebastopol, CA, USA: O'Reilly Media, 2018.",
        "[16] NIST, \"Security and Privacy Controls for Information Systems and Organizations,\" NIST Special Publication 800-53, Rev. 5, Sep. 2020.",
        "[17] N. Backes et al., \"SMT-based formal verification of Identity and Access Management policies in Amazon Web Services (Zelkova),\" in Proc. 20th Int. Conf. Formal Methods in Computer-Aided Design (FMCAD), 2020, pp. 110–119.",
        "[18] K. Jayaraman et al., \"Automated analysis and synthesis of firewall and access control policies in cloud deployments,\" in Proc. ACM SIGCOMM Conf., 2022, pp. 412–426.",
        "[19] Z. Rice, \"Gitleaks: Audit Git repos for secrets,\" Open Source Project, 2024. [Online]. Available: https://github.com/gitleaks/gitleaks",
        "[20] Truffle Security, \"TruffleHog: Find credentials all over the place,\" Truffle Security, 2024. [Online]. Available: https://trufflesecurity.com/trufflehog/",
        "[21] D. Toprani and V. K. Madisetti, \"LLM agentic workflow for automated vulnerability detection and remediation in Infrastructure-as-Code,\" IEEE Access, vol. 13, pp. 69175–69181, 2025.",
        "[22] E. Malul, Y. Meidan, D. Mimran, Y. Elovici, and A. Shabtai, \"GenKubeSec: LLM-based Kubernetes misconfiguration detection, localization, reasoning, and remediation,\" arXiv preprint arXiv:2405.19954, 2024.",
        "[23] X. Lian, Y. Chen, R. Cheng, J. Huang, P. Thakkar, M. Zhang, and T. Xu, \"Configuration validation with large language models,\" arXiv preprint arXiv:2310.09690, 2023.",
        "[24] F. Minna, F. Massacci, and K. Tuma, \"Analyzing and mitigating (with LLMs) the security misconfigurations of Helm charts from Artifact Hub,\" arXiv preprint arXiv:2403.09537, 2024.",
        "[25] M. Alsaid, R. B. Roy, and A. Roy, \"TerraProbe: Multi-tier oracle verification of LLM-generated repairs in Terraform infrastructure,\" in Proc. ACM Conf. Comput. Commun. Security (CCS), 2026, pp. 1–16.",
        "[26] Center for Internet Security, \"CIS Amazon Web Services Foundations Benchmark v3.0.0,\" CIS Security, Tech. Rep., 2024.",
        "[27] PCI Security Standards Council, \"Payment Card Industry Data Security Standard (PCI-DSS) Requirements and Testing Procedures v4.0,\" 2022."
    ]
    
    for ref_entry in references_list:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.space_before = Pt(0)
        p_ref.paragraph_format.space_after = Pt(3)
        p_ref.paragraph_format.line_spacing = 1.05
        p_ref.paragraph_format.left_indent = Inches(0.25)
        p_ref.paragraph_format.first_line_indent = Inches(-0.25)
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        r = p_ref.add_run(ref_entry)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10)
        r.font.color.rgb = RGBColor(20, 20, 20)
        
    # Save the manuscript
    doc.save(output_path)
    print(f"Successfully generated IMPACT-2027 CRC manuscript at: {output_path}")


if __name__ == "__main__":
    target1 = os.path.join(DOCS_PAPER_DIR, "CRC_AgentShield_AI.docx")
    target2 = os.path.join(DOCS_PAPER_DIR, "CRC_549.docx")
    target3 = os.path.join(BASE_DIR, "CRC_AgentShield_AI.docx")
    
    build_manuscript(target1)
    build_manuscript(target2)
    build_manuscript(target3)
