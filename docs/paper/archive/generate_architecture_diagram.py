"""
generate_architecture_diagram.py
Generates a publication-grade, vector-crisp, non-AI architecture diagram for AgentShield AI.
Compliant with IEEE / Springer CCIS specifications (300 DPI, clean vector layout, exact agent flows).
"""

import os
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as patches

matplotlib.rcParams['font.family'] = 'DejaVu Sans'
matplotlib.rcParams['pdf.fonttype'] = 42

out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "paper_figures")
os.makedirs(out_dir, exist_ok=True)
fig_path = os.path.join(out_dir, "fig_architecture_agentshield.png")

fig, ax = plt.subplots(figsize=(11.5, 6.5), dpi=300)
ax.set_xlim(0, 115)
ax.set_ylim(0, 65)
ax.axis('off')

# Background
fig.patch.set_facecolor('#FFFFFF')
ax.set_facecolor('#FFFFFF')

def draw_box(ax, x, y, w, h, title, subtitle, fill, border, title_color='#0F172A', rad=1.5):
    rect = patches.FancyBboxPatch((x, y), w, h, boxstyle=f'round,pad=0.2,rounding_size={rad}',
                                  facecolor=fill, edgecolor=border, linewidth=1.2, zorder=2)
    ax.add_patch(rect)
    ax.text(x + w/2, y + h - 2.2, title, ha='center', va='top', fontsize=8.2, fontweight='bold', color=title_color, zorder=3)
    if subtitle:
        ax.text(x + w/2, y + 1.8, subtitle, ha='center', va='bottom', fontsize=6.8, color='#334155', zorder=3)

def draw_arrow(ax, x1, y1, x2, y2, label='', color='#475569', style='->', lw=1.2, rad=0.0):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw,
                                connectionstyle=f'arc3,rad={rad}', shrinkA=2, shrinkB=2), zorder=4)
    if label:
        mx, my = (x1 + x2)/2, (y1 + y2)/2
        ax.text(mx, my + 1.2, label, ha='center', va='center', fontsize=6.2, fontweight='bold',
                color=color, bbox=dict(boxstyle='round,pad=0.15', facecolor='#FFFFFF', edgecolor='none', alpha=0.9), zorder=5)

# 1. Ingestion Lane
draw_box(ax, 2, 45, 18, 14, 'Input IaC Sources', 'Terraform HCL\nCloudFormation\nKubernetes YAML', '#F1F5F9', '#94A3B8')

# Agent 1
draw_box(ax, 24, 45, 20, 14, 'Agent 1: Orchestrator', 'SHA-256 Validation\nDSL Detection\nContext Graph $\\Gamma$', '#E0F2FE', '#0284C7', '#0369A1')
draw_arrow(ax, 20, 52, 24, 52, 'Raw IaC')

# Agent 2 & Agent 3 (Parallel Analysis)
draw_box(ax, 48, 48, 26, 14, 'Agent 2: CST Parser', 'Tree-sitter C-Bindings\nDependency Graph $G$\nTernary/Dead-Path Pruning', '#FEF3C7', '#D97706', '#92400E')
draw_box(ax, 48, 30, 26, 15, 'Agent 3: Secret Interceptor', '140+ Regex Patterns\nShannon Entropy $H(S) \\geq 4.5$\nCST Scope & Stopwords', '#FEE2E2', '#DC2626', '#991B1B')

draw_arrow(ax, 44, 55, 48, 55, 'CST Scope')
draw_arrow(ax, 44, 48, 48, 38, 'Token Stream', rad=-0.1)

# Agent 4 (Hybrid RAG)
draw_box(ax, 78, 48, 34, 14, 'Agent 4: Compliance RAG', '12,400 CIS/NIST Rules\nQdrant Dense (HNSW 384d)\nSparse BM25 + RRF Fusion', '#EDE9FE', '#7C3AED', '#5B21B6')
draw_arrow(ax, 74, 55, 78, 55, 'Violations $V$')

# Shared Context Graph (Center Banner)
rect_gamma = patches.FancyBboxPatch((24, 18), 50, 8, boxstyle='round,pad=0.2,rounding_size=1.0',
                                    facecolor='#F8FAFC', edgecolor='#64748B', linestyle='--', linewidth=1.0, zorder=1)
ax.add_patch(rect_gamma)
ax.text(49, 22, r'Shared Execution Context Graph $\Gamma = \langle T_{\mathrm{raw}}, \mathcal{H}, \Phi, G, V, \Delta \rangle$',
        ha='center', va='center', fontsize=7.5, fontweight='bold', color='#1E293B', zorder=3)

# Agent 5 (Dual-LLM Consensus)
draw_box(ax, 78, 28, 34, 16, 'Agent 5: Dual-LLM Consensus', 'Claude 3.5 Sonnet (Syntax)\nGPT-4o (Semantics)\n$S_{\\mathrm{dice}} \\geq 0.92$ Consensus', '#CCFBF1', '#0D9488', '#115E59')
draw_arrow(ax, 95, 48, 95, 44, 'Compliance Docs')
draw_arrow(ax, 74, 38, 78, 36, 'Redacted Secrets')

# Agent 6 (Multi-Cloud Sandbox)
draw_box(ax, 48, 2, 36, 14, 'Agent 6: Multi-Cloud Sandbox', 'Tier 1: Syntax (terraform validate)\nTier 2: Execution (LocalStack AWS,\nAzurite Azure, GCP Emulators)', '#FCE7F3', '#DB2777', '#9D174D')
draw_arrow(ax, 78, 33, 66, 16, r'Candidate Patch $\delta$', color='#0D9488', rad=-0.2)

# Feedback Loop (Agent 6 to Agent 5)
draw_arrow(ax, 84, 10, 100, 28, r'Validation Failure (Retry $\leq$ 3)', color='#DC2626', style='->', lw=1.2, rad=0.3)

# Agent 7 & Agent 8 (Output Lane)
draw_box(ax, 6, 2, 38, 14, 'Agent 7 & 8: Compliance & PR', 'Agent 7: MITRE ATT&CK & CWE Mapping\nAgent 8: SARIF JSON Schema\nCryptographic Ed25519 Signed Git PR', '#DCFCE7', '#16A34A', '#14532D')
draw_arrow(ax, 48, 9, 44, 9, r'Verified Patch $\Delta$ ($V_{\mathrm{score}} = 1.0$)', color='#16A34A')

plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
plt.savefig(fig_path, dpi=300, bbox_inches='tight')
plt.close(fig)
print('Successfully generated publication-grade Architecture Diagram:', fig_path)
