"""
build_college_document.py
Generates the complete Project Stage-I documentation in docs/college/PS - Document Format.docx
matching the college index, fixing front matter, populating the List of Figures, and inserting
all diagrams from docs/college/extracted_images/ (derived from Review-AgentSheild-AI.pptx)
with extensive academic text and explanations.
"""

import shutil
from pathlib import Path
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

DOC_PATH = Path("docs/college/PS - Document Format.docx")
BACKUP_PATH = Path("docs/college/PS - Document Format_backup.docx")
IMG_DIR = Path("docs/college/extracted_images")

# Backup the original document if not already backed up
if not BACKUP_PATH.exists():
    shutil.copyfile(DOC_PATH, BACKUP_PATH)
    print(f"Backed up original document to {BACKUP_PATH}")

doc = docx.Document(DOC_PATH)

def format_run(run, font_name="Times New Roman", size_pt=12, bold=False, italic=False, color=None):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
    rPr = run._r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)
    rPr.append(rFonts)

def add_h1(text):
    p = doc.add_paragraph(style='Heading 1')
    p.paragraph_format.space_before = Pt(20)
    p.paragraph_format.space_after = Pt(8)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    format_run(r, font_name="Times New Roman", size_pt=16, bold=True)
    return p

def add_h2(text):
    p = doc.add_paragraph(style='Heading 2')
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    format_run(r, font_name="Times New Roman", size_pt=14, bold=True)
    return p

def add_h3(text):
    p = doc.add_paragraph(style='Heading 3')
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.keep_with_next = True
    r = p.add_run(text)
    format_run(r, font_name="Times New Roman", size_pt=13, bold=True)
    return p

def add_p(text, bold_prefix=None, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(6)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        format_run(r_pre, font_name="Times New Roman", size_pt=12, bold=True)
    r = p.add_run(text)
    format_run(r, font_name="Times New Roman", size_pt=12, bold=False)
    return p

def add_bullet(text, bold_prefix=None):
    p = doc.add_paragraph(style='List Paragraph')
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        r_pre = p.add_run(bold_prefix)
        format_run(r_pre, font_name="Times New Roman", size_pt=12, bold=True)
    r = p.add_run(text)
    format_run(r, font_name="Times New Roman", size_pt=12, bold=False)
    return p

def add_figure(img_filename, caption_text, width_in=6.3):
    img_path = IMG_DIR / img_filename
    if not img_path.exists():
        print(f"Warning: Image {img_path} not found!")
        return None
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(14)
    p_img.paragraph_format.space_after = Pt(4)
    run_img = p_img.add_run()
    run_img.add_picture(str(img_path), width=Inches(width_in))

    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_after = Pt(12)
    p_cap.paragraph_format.keep_with_next = True
    r_cap = p_cap.add_run(caption_text)
    format_run(r_cap, font_name="Times New Roman", size_pt=11, bold=True, italic=True)
    return p_img

print("Step 1: Fixing Front Matter...")

# 1. Cover page title
doc.paragraphs[3].text = "AGENTSHIELD AI: AN AUTONOMOUS MULTI-AGENT FRAMEWORK FOR MULTI-CLOUD INFRASTRUCTURE-AS-CODE SECURITY"
for r in doc.paragraphs[3].runs:
    format_run(r, font_name="Times New Roman", size_pt=16, bold=True)

# 2. Cover page guide
doc.paragraphs[25].text = "Ms. K. Vishal Reddy, Assistant Professor, Department of CSE"
for r in doc.paragraphs[25].runs:
    format_run(r, font_name="Times New Roman", size_pt=12, bold=True)

# 3. Certificate supervisor name
for p in doc.paragraphs[68:75]:
    if "(Ms/Mr XXXX)" in p.text:
        p.text = p.text.replace("(Ms/Mr XXXX)", "(Ms. K. Vishal Reddy)")

# 4. Declaration names & roll numbers
for i in [168, 169, 170]:
    doc.paragraphs[i].text = ""

dec_names_p = doc.paragraphs[167]
dec_names_p.text = (
    "Anisha Paturi\t\t\t\t23BD1A050E\n"
    "Ch Parinamika Bhanu\t\t\t23BD1A0518\n"
    "Ch Venkata Vahini\t\t\t23BD1A051D\n"
    "Sravani Janak\t\t\t\t23BD1A051Y"
)
for r in dec_names_p.runs:
    format_run(r, font_name="Times New Roman", size_pt=12, bold=True)

# 5. Acknowledgement supervisor name
for p in doc.paragraphs[180:185]:
    if "Ms. XXXX" in p.text:
        p.text = p.text.replace("Ms. XXXX", "Ms. K. Vishal Reddy")

# 6. Abstract replacement
abstract_text = (
    "Cloud-native enterprises increasingly rely on Infrastructure-as-Code (IaC) paradigms—such as "
    "Terraform, AWS CloudFormation, Kubernetes manifests, and Helm charts—to automate the provisioning "
    "and orchestration of heterogeneous multi-cloud topologies. However, architectural security misconfigurations "
    "codified at the template layer (such as unrestricted security group ingress rules, unencrypted object "
    "stores, wildcard IAM privilege grants, and hardcoded credentials) propagate instantly into production environments, "
    "accounting for over 73% of cloud enterprise security breaches. Traditional static analysis tools (e.g., Checkov, tfsec, KICS) "
    "suffer from severe syntactic myopia and generate substantial false-positive cascades (32%–48%) due to their inability "
    "to resolve cross-module variable flows and complex resource dependency graphs. Furthermore, existing scanners operate strictly "
    "as diagnostic instruments without automated remediation, resulting in an industry-average Mean Time to Remediation (MTTR) "
    "exceeding 24 days. To address these critical challenges, this project presents AgentShield AI, an autonomous, stateful "
    "multi-agent DevSecOps framework designed for multi-cloud syntactic verification, calibrated secret interception, "
    "consensus-driven dual-LLM remediation, and sandbox-verified patch synthesis. AgentShield AI employs eight specialized "
    "autonomous agents orchestrated over a typed LangGraph execution context graph (Γ). The framework incorporates a polyglot "
    "AST parser dispatcher, a dual-engine secret interceptor combining pattern signatures with Shannon entropy analysis, a hybrid "
    "Retrieval-Augmented Generation (RAG) engine fusing dense Qdrant vector embeddings with sparse BM25 lexical scores via "
    "Reciprocal Rank Fusion (RRF) over CIS and NIST compliance standards, and an LLM consensus engine evaluating cross-model agreement "
    "between frontier models. To guarantee that generated remediations are safe and syntactically sound, candidate patches undergo a "
    "two-tier validation harness combining static linting with simulated LocalStack sandbox runtime dry-runs, equipped with automated "
    "self-healing retry loops. When evaluated on benchmark templates, AgentShield AI delivers high-precision vulnerability detection, "
    "verified Unified Git Diff code patches, attack-path blast radius prioritization, and automated compliance reporting (JSON, Markdown, "
    "HTML, SARIF, and PDF), drastically reducing developer remediation fatigue and elevating cloud security posture."
)
doc.paragraphs[201].text = abstract_text
for r in doc.paragraphs[201].runs:
    format_run(r, font_name="Times New Roman", size_pt=12, bold=False)

print("Step 2: Populating List of Figures Table...")

# Populate Table 1 (List of Figures)
figures_list = [
    ("Figure 1.1", "End-to-End Multi-Agent Architecture Flow of AgentShield AI", "4"),
    ("Figure 1.2", "Six-Stage Subsystem Architecture & Execution Trace", "5"),
    ("Figure 2.1", "Base Research Article in IEEE Access (Toprani & Madisetti, 2025)", "7"),
    ("Figure 2.2", "Base Paper Objective, Architecture, and Performance Benchmark", "8"),
    ("Figure 2.3", "Comparative Analysis of State-of-the-Art Approaches in Literature", "9"),
    ("Figure 2.4", "Existing System Architecture Workflow and Limitations", "10"),
    ("Figure 2.5", "Advantages of the Existing System", "11"),
    ("Figure 2.6", "Architectural Disadvantages and Bottlenecks of Existing Systems", "12"),
    ("Figure 2.7", "Proposed System Objective and Key Pipeline Architecture", "13"),
    ("Figure 2.8", "Architectural Advantages and Dimensional Comparison of Proposed Framework", "14"),
    ("Figure 2.9", "Trade-off and Disadvantage Analysis of Proposed Multi-Agent Approach", "15"),
    ("Figure 3.1", "Software Requirements Specification Functional & Agent Architecture", "18"),
    ("Figure 3.2", "Comprehensive Functional, Non-Functional, and Hardware/Software Requirements", "20"),
    ("Figure 3.3", "High-Level End-to-End System Workflow and Agent State Lifecycle", "23"),
    ("Figure 4.1", "UML Use Case Diagram for AgentShield AI Platform", "27"),
    ("Figure 4.2", "UML Class Diagram & Pydantic Data Contracts Architecture", "29"),
    ("Figure 4.3", "UML Sequence Diagram — Execution Trace from Ingestion to Sandbox Remediation", "32"),
    ("Figure 4.4", "UML Statechart Diagram — Workspace & Remediation Patch Lifecycle", "35"),
    ("Figure 4.5", "UML Deployment Diagram — Containerized Microservices and Cloud Infrastructure", "38")
]

table1 = doc.tables[1]
# Ensure table has enough rows
while len(table1.rows) < len(figures_list) + 1:
    table1.add_row()

for idx, (fig_no, fig_title, page_no) in enumerate(figures_list):
    row_cells = table1.rows[idx + 1].cells
    row_cells[0].text = f"{idx + 1}."
    row_cells[1].text = f"{fig_no}: {fig_title}"
    row_cells[2].text = page_no
    for cell in row_cells:
        for p in cell.paragraphs:
            p.paragraph_format.space_before = Pt(2)
            p.paragraph_format.space_after = Pt(2)
            for r in p.runs:
                format_run(r, font_name="Times New Roman", size_pt=11, bold=False)

print("Step 3: Removing old trailing template paragraphs...")

# Truncate all paragraphs from index 289 to the end
while len(doc.paragraphs) > 289:
    p = doc.paragraphs[-1]
    p._element.getparent().remove(p._element)

print(f"Remaining paragraphs before chapter generation: {len(doc.paragraphs)}")

import sys
sys.path.insert(0, str(Path(__file__).parent))
from write_chapters import append_all_chapters

print("Step 4: Writing all chapters, figures, tables, and sections...")
append_all_chapters(doc)

print("Step 5: Saving completed document...")
doc.save(DOC_PATH)
print(f"Successfully saved complete document to {DOC_PATH}")
