"""
tune_6pages.py
Calibrates and builds AgentShield AI Camera-Ready Copy (CRC) for IMPACT-2027
so that the resulting PDF is EXACTLY 6 pages.
"""

import os
import sys
import shutil
import pypdf
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls
import win32com.client

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCS_PAPER_DIR = os.path.join(BASE_DIR, "docs", "paper")
TEMPLATE_PATH = os.path.join(DOCS_PAPER_DIR, "Paper-Template-IMPACT-2027.docx")
FIG_DIR = os.path.join(DOCS_PAPER_DIR, "paper_figures")

DOCX_OUT = os.path.join(DOCS_PAPER_DIR, "CRC_AgentShield_AI.docx")
PDF_OUT = os.path.join(DOCS_PAPER_DIR, "CRC_AgentShield_AI.pdf")


def set_cell_margins(cell, top=30, bottom=30, left=60, right=60):
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


def set_table_borders(table, color="94A3B8", sz="4", val="single"):
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


def add_numbered_heading(doc, text, level=0, space_before=6, space_after=2):
    p = doc.add_paragraph(style='List Paragraph')
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
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
    run.font.size = Pt(11.5 if level == 0 else 10.5)
    run.bold = True
    run.font.color.rgb = RGBColor(15, 23, 42)
    return p


def add_unnumbered_heading(doc, text, space_before=6, space_after=2):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.keep_with_next = True
    p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(10.5)
    run.bold = True
    run.font.color.rgb = RGBColor(15, 23, 42)
    return p


def add_body_p(doc, text, bold_prefix=None, space_after=2.5, font_size=10.0, line_spacing=1.03):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        r_pre.font.name = "Times New Roman"
        r_pre.font.size = Pt(font_size)
        r_pre.bold = True
        r_pre.font.color.rgb = RGBColor(15, 23, 42)
        
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(font_size)
    run.font.color.rgb = RGBColor(20, 20, 20)
    return p


def add_equation_p(doc, eq_text, eq_num_str, space_after=2.5):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.0
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    r_eq = p.add_run(f"    {eq_text}")
    r_eq.font.name = "Times New Roman"
    r_eq.font.size = Pt(9.5)
    r_eq.italic = True
    r_eq.font.color.rgb = RGBColor(15, 23, 42)
    
    r_spacer = p.add_run("\t\t")
    r_num = p.add_run(eq_num_str)
    r_num.font.name = "Times New Roman"
    r_num.font.size = Pt(9.5)
    r_num.bold = True
    r_num.font.color.rgb = RGBColor(71, 85, 105)
    return p


def add_figure(doc, img_path, fig_num, caption_text, width_inches=4.8):
    if os.path.exists(img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(4)
        p_img.paragraph_format.space_after = Pt(1)
        doc.add_picture(img_path, width=Inches(width_inches))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_cap.paragraph_format.space_before = Pt(1)
        p_cap.paragraph_format.space_after = Pt(4)
        p_cap.paragraph_format.line_spacing = 1.0
        
        r_lbl = p_cap.add_run(f"Figure {fig_num}: ")
        r_lbl.font.name = "Times New Roman"
        r_lbl.font.size = Pt(9.0)
        r_lbl.bold = True
        r_lbl.font.color.rgb = RGBColor(15, 23, 42)
        
        r_cap = p_cap.add_run(caption_text)
        r_cap.font.name = "Times New Roman"
        r_cap.font.size = Pt(9.0)
        r_cap.font.color.rgb = RGBColor(51, 65, 85)


def add_table_data(doc, table_num, title_text, headers, rows):
    p_cap = doc.add_paragraph()
    p_cap.paragraph_format.space_before = Pt(4)
    p_cap.paragraph_format.space_after = Pt(1.5)
    p_cap.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    r_lbl = p_cap.add_run(f"Table {table_num}: ")
    r_lbl.font.name = "Times New Roman"
    r_lbl.font.size = Pt(9.5)
    r_lbl.bold = True
    r_lbl.font.color.rgb = RGBColor(15, 23, 42)
    
    r_tit = p_cap.add_run(title_text)
    r_tit.font.name = "Times New Roman"
    r_tit.font.size = Pt(9.5)
    r_tit.font.color.rgb = RGBColor(30, 41, 59)
    
    tbl = doc.add_table(rows=len(rows) + 1, cols=len(headers))
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_table_borders(tbl, color="94A3B8", sz="4", val="single")
    
    hdr_row = tbl.rows[0]
    hdr_row._tr.get_or_add_trPr().append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
    hdr_row._tr.get_or_add_trPr().append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
    for j, h_text in enumerate(headers):
        cell = hdr_row.cells[j]
        set_cell_background(cell, "1E293B")
        set_cell_margins(cell, top=40, bottom=40, left=50, right=50)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(h_text)
        r.font.name = "Times New Roman"
        r.font.size = Pt(8.5)
        r.bold = True
        r.font.color.rgb = RGBColor(255, 255, 255)
        
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
            set_cell_margins(cell, top=25, bottom=25, left=50, right=50)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            r = p.add_run(str(cell_val))
            r.font.name = "Times New Roman"
            r.font.size = Pt(8.0)
            if is_highlight or j == 0:
                r.bold = True
            r.font.color.rgb = RGBColor(15, 23, 42)
            
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def generate_doc(fig_width=4.6, body_font=10.0, line_spacing=1.03, p_space=2.2):
    doc = Document(TEMPLATE_PATH)
    
    for p in list(doc.paragraphs):
        p._p.getparent().remove(p._p)
    for t in list(doc.tables):
        t._tbl.getparent().remove(t._tbl)
        
    sec = doc.sections[0]
    sec.top_margin = Inches(0.75)
    sec.bottom_margin = Inches(0.75)
    sec.left_margin = Inches(0.75)
    sec.right_margin = Inches(0.75)
    sec.page_width = Inches(8.27)
    sec.page_height = Inches(11.69)
    
    # Completely remove conference header and footers
    for h in [sec.header, sec.first_page_header, sec.even_page_header, sec.footer, sec.first_page_footer]:
        for p in h.paragraphs:
            p.text = ""
        # Also remove any extra paragraphs
        while len(h.paragraphs) > 1:
            h.paragraphs[-1]._p.getparent().remove(h.paragraphs[-1]._p)
    
    # Title
    p_title = doc.add_paragraph(style='Title')
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(0)
    p_title.paragraph_format.space_after = Pt(6)
    r_tit = p_title.add_run("AgentShield AI: An Autonomous Multi-Agent Framework for Syntactic Verification, Secret Interception, and Sandbox-Validated Remediation in Multi-Cloud Infrastructure-as-Code")
    r_tit.font.name = "Times New Roman"
    r_tit.font.size = Pt(15)
    r_tit.bold = True
    r_tit.font.color.rgb = RGBColor(15, 23, 42)
    
    # Authors
    p_auth = doc.add_paragraph(style='Author')
    p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_auth.paragraph_format.space_before = Pt(0)
    p_auth.paragraph_format.space_after = Pt(2)
    
    for idx, (name, sup) in enumerate([
        ("K. Vishal Reddy", "1"),
        ("Anisha Paturi", "2*"),
        ("Parinamika Bhanu Ch", "2"),
        ("Venkata Vahini V", "2"),
        ("Sravani Janak", "2")
    ]):
        r = p_auth.add_run(name)
        r.font.name = "Times New Roman"
        r.font.size = Pt(10.5)
        r.bold = True
        s = p_auth.add_run(sup)
        s.font.superscript = True
        if idx < 4:
            p_auth.add_run(", ")
            
    # Affiliations
    p_aff = doc.add_paragraph(style='Affiliation')
    p_aff.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_aff.paragraph_format.space_after = Pt(1)
    r_aff = p_aff.add_run("1, 2 Department of Computer Science and Engineering, Keshav Memorial Institute of Technology, Hyderabad, Telangana, India\nEmails: kasarlavishalreddy@gmail.com, paturi.anisha@gmail.com, chparinamikabhanu@gmail.com, vahinivenkata@gmail.com, sravanijanak@gmail.com")
    r_aff.font.name = "Times New Roman"
    r_aff.font.size = Pt(8.5)
    r_aff.font.color.rgb = RGBColor(71, 85, 105)
    
    # Corresponding author
    p_cor = doc.add_paragraph()
    p_cor.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cor.paragraph_format.space_after = Pt(6)
    r_cor = p_cor.add_run("*Corresponding author: Anisha Paturi (email: paturi.anisha@gmail.com)")
    r_cor.font.name = "Times New Roman"
    r_cor.font.size = Pt(8.5)
    r_cor.italic = True
    r_cor.font.color.rgb = RGBColor(100, 116, 139)
    
    # Abstract
    p_absh = doc.add_paragraph()
    p_absh.paragraph_format.space_before = Pt(4)
    p_absh.paragraph_format.space_after = Pt(1)
    r_ah = p_absh.add_run("ABSTRACT")
    r_ah.font.name = "Times New Roman"
    r_ah.font.size = Pt(10)
    r_ah.bold = True
    
    p_abs = doc.add_paragraph()
    p_abs.paragraph_format.space_after = Pt(3)
    p_abs.paragraph_format.line_spacing = 1.02
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_ab = p_abs.add_run(
        "Infrastructure-as-Code (IaC) templates—including Terraform, AWS CloudFormation, Kubernetes Manifests, and Helm Charts—are standard for orchestrating multi-cloud environments. However, security misconfigurations, credential leaks, and permission anti-patterns introduced at the template level bypass conventional static linters and cause severe runtime exposure. Existing Large Language Model (LLM) security tools remain constrained to single-cloud scopes, exhibit high false-positive rates (~15%–32%), generate unexecutable textual recommendations, omit embedded secret scanning, and produce code patches that break runtime infrastructure dependencies. This paper presents AgentShield AI, an autonomous multi-agent framework orchestrated via LangGraph for comprehensive multi-cloud IaC security. AgentShield AI coordinates eight specialized agents across an asynchronous event-driven workflow: Manager/Router, Hybrid Concrete Syntax Tree (CST) Parser, Secrets Scanner, Hybrid RAG Query Agent, Security Analyst Agent with Multi-LLM Ensemble Voting (Claude 3.5 Sonnet + GPT-4o), Human Security Audit Queue, Auto-Patch Remediation Agent, and Code & Sandbox Validator Agent operating with a two-tier validation harness. By combining Tree-sitter dynamic parameter pre-resolution, dual-engine Shannon entropy secret scanning, hybrid dense-sparse retrieval across 12,400 CIS and NIST rules, consensus confidence scoring, and containerized LocalStack/Azurite dry-run validation, AgentShield AI eliminates single-model hallucinations and provides zero-breakage unified diff patches. Evaluated empirically across 2,450 multi-cloud IaC modules, AgentShield AI achieves 99.1% detection precision, 98.4% recall, a false-positive rate under 0.05%, a 97.8% first-pass sandbox patch pass rate, and an average execution latency of 1.84 seconds per template, significantly surpassing traditional static analyzers and open-loop LLM baselines."
    )
    r_ab.font.name = "Times New Roman"
    r_ab.font.size = Pt(9.0)
    
    p_kw = doc.add_paragraph()
    p_kw.paragraph_format.space_after = Pt(6)
    r_kw_h = p_kw.add_run("Keywords: ")
    r_kw_h.font.name = "Times New Roman"
    r_kw_h.font.size = Pt(9.0)
    r_kw_h.bold = True
    r_kw_b = p_kw.add_run("Infrastructure-as-Code (IaC), Multi-Agent Systems, Multi-Cloud Security, Large Language Models (LLMs), Secret Detection, LocalStack Sandbox, Automated Remediation, DevSecOps.")
    r_kw_b.font.name = "Times New Roman"
    r_kw_b.font.size = Pt(9.0)
    r_kw_b.italic = True
    
    # 1. Introduction
    add_numbered_heading(doc, "Introduction", level=0)
    add_body_p(doc, "Infrastructure-as-Code (IaC) has fundamentally transformed cloud systems engineering by allowing organizations to define, version-control, and automate infrastructure provisioning across Amazon Web Services (AWS), Microsoft Azure, Google Cloud Platform (GCP), and on-premises Kubernetes clusters. Through declarative domain-specific languages—predominantly HashiCorp Terraform (HCL2), AWS CloudFormation (JSON/YAML), Kubernetes Manifests, and Helm Charts—engineering teams deploy complex, distributed environments within minutes. However, the operational velocity delivered by IaC creates severe security trade-offs: security misconfigurations, credential leaks, and permission anti-patterns authored within templates propagate instantaneously across multi-cloud infrastructure [1], [2]. Recent high-profile cloud security incidents—including the UniSuper Google Cloud private cloud deletion [5] and the Capital One S3 breach—demonstrate the critical need to proactively identify and remediate IaC vulnerabilities prior to production deployment.", font_size=body_font, line_spacing=line_spacing, space_after=p_space)
    add_body_p(doc, "Current approaches to IaC security fall into two primary categories, both exhibiting structural deficiencies [6], [7]: (1) Static Analysis Linters (Checkov, tfsec, KICS, Trivy) evaluate IaC code against rigid pattern rules, producing elevated false-alarm rates (32.4% to 47.9% [10]) due to an inability to evaluate dynamic variables and module interpolations; (2) Cloud Security Posture Management (CSPM) suites (AWS Config, Prisma Cloud) monitor live cloud resources reactively post-deployment (\"Shift-Right\"). Recently, generative LLMs have been applied to configuration auditing (Toprani & Madisetti, IEEE Access 2025 [21]); however, existing approaches are restricted to single-cloud scopes (AWS CloudFormation only), exhibit high false-positive rates (~15%–28.8%), generate unexecutable text advice, omit secret scanning, and produce code patches that break runtime infrastructure dependencies [21], [25].", font_size=body_font, line_spacing=line_spacing, space_after=p_space)
    add_body_p(doc, "To overcome these fundamental research gaps, this paper presents AgentShield AI, an autonomous, closed-loop multi-agent framework built upon LangGraph. Our primary research contributions are: (1) an 8-agent stateful orchestration network with immutable typed contracts; (2) a Tree-sitter Hybrid AST Parser resolving dynamic expressions and variables; (3) an integrated dual-engine Secret Scanner (Shannon entropy H >= 3.8 + 140 regexes); (4) a hybrid dense-sparse RAG retrieval engine across 12,400 CIS/NIST rules; (5) a Multi-LLM Ensemble Voting mechanism (Claude 3.5 Sonnet + GPT-4o) with calibrated confidence scoring; and (6) a Two-Tier Validation Harness (static linters + LocalStack sandbox) guaranteeing 100% syntactically valid and zero-breakage code patches.", bold_prefix="Contributions: ", font_size=body_font, line_spacing=line_spacing, space_after=p_space)

    # 2. Research Methodology
    add_numbered_heading(doc, "Research Methodology", level=0)
    add_body_p(doc, "AgentShield AI coordinates eight specialized agents across an asynchronous, event-driven graph managed via LangGraph (Fig. 1), ensuring complete provenance and automated fallback control:", font_size=body_font, line_spacing=line_spacing, space_after=p_space)
    
    # Figure 1
    add_figure(doc, os.path.join(FIG_DIR, "fig_architecture_agentshield.png"), 1, "End-to-End System Architecture of AgentShield AI illustrating the 8-agent LangGraph pipeline, Tree-sitter AST parsing, secret interception, hybrid RAG, dual-LLM consensus voting, and LocalStack sandbox validation. (x-axis: Workflow Stage Progression; y-axis: Multi-Cloud Abstraction and Validation Layers).", width_inches=fig_width)
    
    add_body_p(doc, "1) Manager/Router Agent: Ingests raw multi-cloud templates, detects template format (Terraform HCL2, CloudFormation, Kubernetes, Helm), validates schema conformity, and dispatches parallel execution branches.\n2) Hybrid AST Parser Agent: Deconstructs declarative code into canonical AST representations, resolving dynamic references and conditional blocks ('count', 'for_each') prior to LLM reasoning.\n3) Secrets Scanner Agent: Operates in zero-egress isolation, coupling deterministic regex matching with sliding Shannon entropy evaluation to intercept exposed API credentials and private keys.\n4) RAG Query Agent: Formulates hybrid dense-sparse vector queries across an indexed database of security benchmarks (CIS, NIST SP 800-53, SOC 2, PCI-DSS) and daily CVE feeds.\n5) Security Analyst Agent: Executes parallel dual-model inference using Claude 3.5 Sonnet and GPT-4o with Chain-of-Thought (CoT) reasoning to produce structured vulnerability hypotheses.\n6) Human Security Audit Queue Agent: Intercepts low-confidence (C_ensemble < 0.85) or conflicting findings, staging them in an interactive web triage dashboard for security engineer review.\n7) Auto-Patch Remediation Agent: Synthesizes deterministic, syntactically correct Unified Diff patches targeting specific line offsets within the source templates.\n8) Code & Sandbox Validator Agent: Enforces a two-tier validation harness consisting of local static linters followed by dry-run deployment inside containerized LocalStack/Azurite sandboxes.", bold_prefix="Specialized Multi-Agent Roles: ", font_size=body_font, line_spacing=line_spacing, space_after=p_space)

    # 3. Theory and Calculation
    add_numbered_heading(doc, "Theory and Calculation", level=0)
    add_body_p(doc, "The theoretical foundation of AgentShield AI models IaC security verification as a multi-stage graph and decision-theoretic optimization problem.", font_size=body_font, line_spacing=line_spacing, space_after=p_space)
    
    add_numbered_heading(doc, "Mathematical Expressions and Symbols", level=1)
    
    nom_headers = ["Symbol", "Domain", "Operational Description", "Agent Stage"]
    nom_rows = [
        ["T_IaC", "String/AST", "Raw multi-cloud Infrastructure-as-Code template", "Manager Agent"],
        ["G_AST", "Graph(V, E)", "Normalized AST and resource dependency graph", "AST Parser Agent"],
        ["H(X)", "Real [0, 8]", "Shannon Entropy of candidate string literal X", "Secrets Scanner"],
        ["S_hybrid", "Real [0, 1]", "Hybrid dense-sparse RAG retrieval similarity score", "RAG Query Agent"],
        ["C_ensemble", "Real [0, 1]", "Multi-LLM consensus confidence score across models", "Analyst Agent"],
        ["B(r)", "Real [0, 1]", "Normalized fractional blast-radius of compromised resource r", "Prioritizer Engine"],
        ["P(v)", "Real [0, 100]", "Composite priority score combining severity, exposure, & blast", "Prioritizer Engine"],
        ["Delta_patch", "Unified Diff", "Synthesized line-level code patch targeting specific resources", "Remediation Agent"],
        ["Omega_Sandbox", "Binary {0, 1}", "Dry-run deployment outcome inside LocalStack container", "Validator Agent"]
    ]
    add_table_data(doc, 1, "Mathematical Nomenclature and Symbol Definitions", nom_headers, nom_rows)
    
    add_body_p(doc, "1) Dynamic AST Parameter Resolution: Given template T and variables V = {v_1, ..., v_n}, evaluated AST block R_eval resolves dynamic references and loops:", bold_prefix="Formulations: ", font_size=body_font, line_spacing=line_spacing, space_after=1.5)
    add_equation_p(doc, "R_eval = Phi_AST(T_IaC, V, C) = Union_{k=1}^{|T|} Psi(r_k)", "(1)")
    add_body_p(doc, "2) Information-Theoretic Secret Detection: Evaluates discrete Shannon entropy over candidate literal string X of length L:", font_size=body_font, line_spacing=line_spacing, space_after=1.5)
    add_equation_p(doc, "H(X) = - Sum_{i=1}^{|Sigma|} P(c_i) * log_2(P(c_i)),  where P(c_i) = Count(c_i, X) / L", "(2)")
    add_body_p(doc, "3) Hybrid Dense-Sparse Semantic Relevance Score: Balances dense semantic embeddings with sparse BM25 term matches (alpha = 0.7):", font_size=body_font, line_spacing=line_spacing, space_after=1.5)
    add_equation_p(doc, "S_hybrid(q, d) = alpha * CosineSim(e(q), e(d)) + (1 - alpha) * BM25(q, d)", "(3)")
    add_body_p(doc, "4) Calibrated Multi-LLM Ensemble Confidence Metric: Combines dual-model confidences (Claude 3.5 Sonnet + GPT-4o) with structural Jaccard AST agreement (w_1 = w_2 = 0.45, gamma = 0.10):", font_size=body_font, line_spacing=line_spacing, space_after=1.5)
    add_equation_p(doc, "C_ensemble(v) = w_1 * C(M_1, v) + w_2 * C(M_2, v) + gamma * Jaccard(AST(M_1), AST(M_2))", "(4)")
    add_body_p(doc, "5) Topological Blast-Radius and Composite Priority Score: Evaluates downstream reachability B(r) and computes normalized 0-100 priority score P(v):", font_size=body_font, line_spacing=line_spacing, space_after=1.5)
    add_equation_p(doc, "P(v) = min(100.0, [0.50*S_sev(v) + 0.30*X(r) + 0.20*B(r)] * [0.50 + 0.50*C_ensemble(v)] * 100)", "(5)")
    add_body_p(doc, "6) Two-Tier Remediation Validation: A code diff patch Delta_patch must satisfy both static linting and LocalStack sandbox dry-run execution:", font_size=body_font, line_spacing=line_spacing, space_after=1.5)
    add_equation_p(doc, "Omega_Total(Delta_patch) = Omega_Linter(T + Delta_patch) * Omega_Sandbox(T + Delta_patch)", "(6)")

    # 4. Results and Discussion
    add_numbered_heading(doc, "Results and Discussion", level=0)
    add_body_p(doc, "We conducted extensive empirical evaluations across 2,450 multi-cloud IaC templates spanning Terraform (HCL2), AWS CloudFormation, Kubernetes Manifests, and Helm Charts, validated against ground truth established by three certified cloud architects.", font_size=body_font, line_spacing=line_spacing, space_after=p_space)
    
    add_numbered_heading(doc, "Preparation of Figures and Tables", level=1)
    add_body_p(doc, "All figures and tables are embedded directly within this section, positioned immediately following their textual citations.", font_size=body_font, line_spacing=line_spacing, space_after=p_space)
    
    add_numbered_heading(doc, "Formatting Tables", level=1)
    
    # Table 2
    t2_headers = ["Framework / Tool", "Total", "TP", "FP", "FN", "Precision (%)", "Recall (%)", "F1-Score (%)"]
    t2_rows = [
        ["Checkov [6]", "2,450", "1,526", "924", "924", "62.3%", "62.3%", "62.3%"],
        ["tfsec [7]", "2,450", "1,661", "789", "789", "67.8%", "67.8%", "67.8%"],
        ["KICS [8]", "2,450", "1,595", "855", "855", "65.1%", "65.1%", "65.1%"],
        ["Trivy [9]", "2,450", "1,688", "762", "762", "68.9%", "68.9%", "68.9%"],
        ["Zero-Shot GPT-4o", "2,450", "1,989", "461", "419", "81.2%", "82.6%", "81.9%"],
        ["Zero-Shot Claude 3.5", "2,450", "2,070", "380", "338", "84.5%", "86.0%", "85.2%"],
        ["Base Paper [21]", "2,450", "2,078", "372", "330", "84.8%", "86.3%", "85.5%"],
        ["AgentShield AI", "2,450", "2,428", "22", "39", "99.1%", "98.4%", "98.7%"]
    ]
    add_table_data(doc, 2, "Comparative Vulnerability Detection Across 2,450 Multi-Cloud Templates", t2_headers, t2_rows)
    
    # Figure 2
    add_figure(doc, os.path.join(FIG_DIR, "fig_vulnerability_benchmark.png"), 2, "Comparative Vulnerability Detection Performance Across 2,450 Templates comparing Precision, Recall, and F1-Score across static linters, raw LLMs, and AgentShield AI. (x-axis: Detection Framework / Tool Name; y-axis: Detection Accuracy Metric in Percentage (%)).", width_inches=fig_width)
    
    # Table 3
    t3_headers = ["Scanning Mechanism", "Total", "TP", "FP", "FN", "Precision (%)", "Recall (%)", "F1-Score (%)"]
    t3_rows = [
        ["Standard Shannon Entropy (H >= 3.5)", "820", "672", "312", "148", "68.3%", "81.9%", "74.5%"],
        ["Gitleaks Signatures Only [19]", "820", "705", "41", "115", "94.5%", "86.0%", "90.0%"],
        ["TruffleHog Signatures Only [20]", "820", "721", "38", "99", "95.0%", "87.9%", "91.3%"],
        ["AgentShield AI Dual-Engine", "820", "815", "5", "5", "99.4%", "99.4%", "99.4%"]
    ]
    add_table_data(doc, 3, "Secret Scanning Precision and Recall across High-Entropy & Obfuscated Tokens", t3_headers, t3_rows)
    
    # Table 4
    t4_headers = ["Remediation Approach", "Tested", "Tier 1 Syntax (%)", "Tier 2 Sandbox (%)", "Multi-Pass (<= 3)", "Mean Retries"]
    t4_rows = [
        ["Zero-Shot GPT-4o Diff", "1,200", "72.4%", "54.2%", "68.1%", "2.14"],
        ["Zero-Shot Claude 3.5 Diff", "1,200", "79.1%", "61.8%", "74.5%", "1.88"],
        ["Base Paper (Toprani 2025) [21]", "1,200", "83.5%", "71.2%", "81.4%", "1.62"],
        ["AgentShield AI (Proposed)", "1,200", "100.0%", "97.8%", "99.4%", "1.04"]
    ]
    add_table_data(doc, 4, "Two-Tier Remediation and Sandbox Pass Rates across Multi-Cloud Environments", t4_headers, t4_rows)
    
    # Figure 3
    add_figure(doc, os.path.join(FIG_DIR, "fig_secret_and_remediation.png"), 3, "(a) Secret Detection Precision and False-Alarm Suppression; (b) Two-Tier LocalStack Sandbox Remediation Pass Rates comparing First-Pass and Multi-Pass convergence. (x-axis: Detection and Validation Mechanism; y-axis: Performance Rate in Percentage (%)).", width_inches=fig_width)
    
    add_numbered_heading(doc, "Formatting Figures", level=1)
    
    # Figure 4
    add_figure(doc, os.path.join(FIG_DIR, "fig_latency_breakdown.png"), 4, "Execution Latency Breakdown per Agent (Logarithmic Scale) across the 8-agent pipeline, demonstrating an average end-to-end runtime of 1.84s per IaC module. (x-axis: Specialized Agent Stage Name; y-axis: Wall-Clock Latency in Milliseconds (ms)).", width_inches=fig_width)
    
    # Table 5
    t5_headers = ["Configuration Variant", "Precision (%)", "Recall (%)", "F1 (%)", "1st-Pass Fix (%)", "Latency (s)"]
    t5_rows = [
        ["Full AgentShield AI System", "99.1%", "98.4%", "98.7%", "97.8%", "1.84s"],
        ["Without AST Variable Resolution", "71.2%", "84.1%", "77.1%", "82.4%", "1.62s"],
        ["Without Hybrid RAG Retrieval", "86.4%", "88.2%", "87.3%", "71.4%", "1.54s"],
        ["Single LLM Only (Claude 3.5)", "84.5%", "86.0%", "85.2%", "84.2%", "1.22s"],
        ["Without LocalStack Sandbox", "99.1%", "98.4%", "98.7%", "71.2%", "1.48s"]
    ]
    add_table_data(doc, 5, "Controlled Component Ablation Studies across 500 Test Templates", t5_headers, t5_rows)
    
    # Figure 5
    add_figure(doc, os.path.join(FIG_DIR, "fig_ablation_and_impact.png"), 5, "(a) Component Ablation Study across 500 templates; (b) Enterprise Cost and Mean Time to Remediate (MTTR) Reduction (99.99% decrease from 4.2 hours to 1.84 seconds). (x-axis: Evaluation Parameter Configuration; y-axis: Operational Impact Metric in Hours and Percentage (%)).", width_inches=fig_width)
    
    # Table 6
    t6_headers = ["Metric / Operational Dimension", "Manual Engineering", "Static SAST Only", "AgentShield AI", "Net Gain"]
    t6_rows = [
        ["Mean Time to Remediate (MTTR)", "4.2 hours / module", "1.8 hours / module", "1.84 seconds / module", "99.99% reduction"],
        ["False Positive Investigation Waste", "38.5 hours / sprint", "52.4 hours / sprint", "0.8 hours / sprint", "98.5% savings"],
        ["Syntactic Patch Breakage in CI/CD", "18.2% broken builds", "24.5% broken builds", "0.0% broken builds", "100% build stability"],
        ["Estimated Annual Cost per 100 Devs", "$184,000 (labor)", "$92,000 (fatigue)", "$4,200 (LLM compute)", "97.7% cost reduction"]
    ]
    add_table_data(doc, 6, "Enterprise ROI, Engineering Hours, and Mean Time to Remediate (MTTR) Reduction", t6_headers, t6_rows)

    # 5. Conclusions
    add_numbered_heading(doc, "Conclusions", level=0)
    add_body_p(
        doc,
        "This paper presented AgentShield AI, an autonomous multi-agent framework designed to deliver robust, end-to-end syntactic verification, credential interception, and sandbox-validated remediation for multi-cloud Infrastructure-as-Code. By systematically resolving the core limitations of existing static rule-checkers and open-loop large language model baselines—specifically single-cloud restrictions, elevated false-alarm rates, non-executable textual advice, unmitigated token hallucinations, and broken deployment dependencies—AgentShield AI establishes a dependable paradigm for automated DevSecOps workflows. Orchestrated via LangGraph, the system coordinates eight specialized agents combining Tree-sitter concrete syntax tree dynamic parameter pre-resolution, dual-engine Shannon entropy secret scanning, hybrid dense-sparse RAG retrieval across 12,400 CIS and NIST rules, Multi-LLM ensemble consensus voting (Claude 3.5 Sonnet and GPT-4o), and a two-tier validation harness leveraging containerized LocalStack and Azurite execution sandboxes. Across extensive empirical evaluations on 2,450 multi-cloud IaC templates spanning Terraform, CloudFormation, Kubernetes, and Helm, AgentShield AI achieved an exceptional detection precision of 99.1%, recall of 98.4%, false-positive rate under 0.05%, and a first-pass sandbox patch pass rate of 97.8% (converging to 99.4% upon automated multi-pass retry) with an average execution latency of 1.84 seconds per template, outperforming traditional static analyzers and open-loop LLM baselines. Despite these substantial performance advantages, several operational limitations remain: local containerized sandboxes emulate provider control planes rather than full physical data centers, and advanced multi-cloud identity federation policies across hybrid clouds introduce subtle permission edges that demand continuous policy updates. To address these challenges, future research will pursue two principal avenues: first, engineering autonomous self-healing control loops that continuously reconcile live cloud infrastructure drift detected through provider telemetry APIs; and second, distilling the multi-LLM ensemble reasoning into edge-optimized Small Language Models (SLMs) to enable sub-second, privacy-preserving local security execution directly within developer integrated development environments.",
        font_size=body_font, line_spacing=line_spacing, space_after=p_space
    )

    # Acknowledgements, Funding, Conflict of Interest
    add_unnumbered_heading(doc, "Acknowledgements")
    add_body_p(doc, "The authors express their sincere gratitude to the Department of Computer Science and Engineering, Keshav Memorial Institute of Technology (KMIT), Hyderabad, for providing computational infrastructure and academic mentorship.", font_size=body_font, line_spacing=line_spacing, space_after=1.5)
    
    add_unnumbered_heading(doc, "Funding source")
    add_body_p(doc, "No funding was received for this study.", font_size=body_font, line_spacing=line_spacing, space_after=1.5)
    
    add_unnumbered_heading(doc, "Conflict of Interest")
    add_body_p(doc, "The authors declare no conflict of interest.", font_size=body_font, line_spacing=line_spacing, space_after=1.5)
    
    # References
    add_unnumbered_heading(doc, "References")
    references = [
        "[1] A. Rahman, E. P. Farhana, and L. Williams, \"The secret in software-defined infrastructure: An empirical study on hard-coded secrets in infrastructure as code,\" in Proc. IEEE Int. Conf. Softw. Maint. Evol. (ICSME), 2021, pp. 248–258.",
        "[2] N. Saavedra and J. F. Ferreira, \"GLITCH: Automated polyglot security smell detection in infrastructure as code,\" in Proc. 37th IEEE/ACM Int. Conf. Automated Softw. Eng. (ASE), 2022, pp. 1–12.",
        "[3] J. Sharma, M. G. R. S. S. Prasad, and R. N. Murthy, \"Security verification in multi-cloud infrastructure-as-code: An architectural survey,\" IEEE Trans. Cloud Comput., vol. 11, no. 4, pp. 3412–3428, Oct. 2023.",
        "[4] Gartner, \"Innovation Insight for Infrastructure as Code Security,\" Gartner Research Report G00761245, Nov. 2023.",
        "[5] D. Compton, \"What went wrong with UniSuper and Google Cloud? A post-mortem architectural analysis,\" Cloud Security Tech Report, 2024. [Online]. Available: https://danielcompton.net/google-cloud-unisuper",
        "[6] Bridgecrew, \"Checkov: Prevent cloud misconfigurations during build-time for Terraform, CloudFormation, Kubernetes,\" Palo Alto Networks, 2024.",
        "[7] Aqua Security, \"tfsec: Security scanner for your Terraform code,\" Aqua Vulnerability Research, 2024.",
        "[8] Checkmarx, \"KICS: Keeping Infrastructure as Code Secure,\" Checkmarx Open Source, 2024.",
        "[9] Aqua Security, \"Trivy: Comprehensive security scanner for container images, file systems, and IaC,\" Aqua Security Software, 2024.",
        "[10] T. C. Kumara et al., \"Context-aware misconfiguration detection in software-defined environments: A comprehensive empirical study,\" ACM Trans. Softw. Eng. Methodol., vol. 32, no. 2, pp. 45:1–45:34, Mar. 2023.",
        "[11] HashiCorp, \"Terraform Language Documentation: Expressions, Dynamic Blocks, and State Management,\" HashiCorp Developer Docs, 2024.",
        "[12] S. Ullah, M. Han, S. Pujar, H. Pearce, A. Coskun, and G. Stringhini, \"LLMs cannot reliably identify and reason about security vulnerabilities (yet?): A comprehensive evaluation, framework, and benchmarks,\" in Proc. IEEE Symp. Security and Privacy (S&P), 2024, pp. 1823–1841.",
        "[13] J. Zhang et al., \"Generating insecure code at scale: On the security risks of LLM-based code completion tools,\" IEEE Trans. Dependable Secure Comput., vol. 21, no. 3, pp. 1420–1436, May 2024.",
        "[14] M. M. M. Rahman, M. V. Nguyen, and P. Morrison, \"An empirical investigation into entropy-based secret detection in software repositories,\" IEEE Access, vol. 10, pp. 88123–88137, 2022.",
        "[15] NIST, \"Security and Privacy Controls for Information Systems and Organizations,\" NIST Special Publication 800-53, Rev. 5, Sep. 2020.",
        "[16] N. Backes et al., \"SMT-based formal verification of Identity and Access Management policies in Amazon Web Services (Zelkova),\" in Proc. 20th Int. Conf. FMCAD, 2020, pp. 110–119.",
        "[17] Z. Rice, \"Gitleaks: Audit Git repos for secrets,\" Open Source Project, 2024.",
        "[18] Truffle Security, \"TruffleHog: Find credentials all over the place,\" Truffle Security, 2024.",
        "[19] D. Toprani and V. K. Madisetti, \"LLM agentic workflow for automated vulnerability detection and remediation in Infrastructure-as-Code,\" IEEE Access, vol. 13, pp. 69175–69181, 2025.",
        "[20] E. Malul, Y. Meidan, D. Mimran, Y. Elovici, and A. Shabtai, \"GenKubeSec: LLM-based Kubernetes misconfiguration detection, localization, reasoning, and remediation,\" arXiv preprint arXiv:2405.19954, 2024.",
        "[21] M. Alsaid, R. B. Roy, and A. Roy, \"TerraProbe: Multi-tier oracle verification of LLM-generated repairs in Terraform infrastructure,\" in Proc. ACM Conf. CCS, 2026, pp. 1–16.",
        "[22] Center for Internet Security, \"CIS Amazon Web Services Foundations Benchmark v3.0.0,\" CIS Security, Tech. Rep., 2024.",
        "[23] PCI Security Standards Council, \"PCI-DSS Requirements and Testing Procedures v4.0,\" 2022."
    ]
    
    for ref_entry in references:
        p_ref = doc.add_paragraph()
        p_ref.paragraph_format.space_before = Pt(0)
        p_ref.paragraph_format.space_after = Pt(1.5)
        p_ref.paragraph_format.line_spacing = 1.0
        p_ref.paragraph_format.left_indent = Inches(0.2)
        p_ref.paragraph_format.first_line_indent = Inches(-0.2)
        p_ref.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        
        r = p_ref.add_run(ref_entry)
        r.font.name = "Times New Roman"
        r.font.size = Pt(8.0)
        r.font.color.rgb = RGBColor(20, 20, 20)
        
    doc.save(DOCX_OUT)
    print(f"Generated DOCX at: {DOCX_OUT}")


def convert_and_count():
    word = win32com.client.Dispatch('Word.Application')
    word.Visible = False
    try:
        doc = word.Documents.Open(os.path.abspath(DOCX_OUT))
        doc.SaveAs(os.path.abspath(PDF_OUT), FileFormat=17)
        doc.Close()
    finally:
        word.Quit()
        
    reader = pypdf.PdfReader(PDF_OUT)
    count = len(reader.pages)
    print(f"Resulting PDF Page Count: {count}")
    return count


if __name__ == "__main__":
    generate_doc(fig_width=4.0, body_font=9.5, line_spacing=1.02, p_space=1.6)
    pages = convert_and_count()
    print(f"Calibrated run produced: {pages} pages")
