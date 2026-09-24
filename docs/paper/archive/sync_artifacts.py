# -*- coding: utf-8 -*-
import os
import shutil
import zipfile
import pypdf

base_dir = os.path.dirname(os.path.abspath(__file__))

sample_tex = os.path.join(base_dir, 'samplepaper.tex')
sample_pdf = os.path.join(base_dir, 'samplepaper.pdf')

paul_tex = os.path.join(base_dir, 'AgentShield_AI_PAUL2026_Revised.tex')
paul_pdf = os.path.join(base_dir, 'AgentShield_AI_PAUL2026_Revised.pdf')
springer_pdf = os.path.join(base_dir, 'AgentShield_AI_Springer_Conference_Paper.pdf')

# 1. Sync tex
shutil.copyfile(sample_tex, paul_tex)

# 2. Sync pdfs
shutil.copyfile(sample_pdf, paul_pdf)
shutil.copyfile(sample_pdf, springer_pdf)

# 3. Verify page counts
reader = pypdf.PdfReader(sample_pdf)
print(f"samplepaper.pdf total pages: {len(reader.pages)}")
assert len(reader.pages) <= 15, f"Expected <= 15 pages, got {len(reader.pages)}"

reader_paul = pypdf.PdfReader(paul_pdf)
print(f"AgentShield_AI_PAUL2026_Revised.pdf total pages: {len(reader_paul.pages)}")
assert len(reader_paul.pages) <= 15

reader_springer = pypdf.PdfReader(springer_pdf)
print(f"AgentShield_AI_Springer_Conference_Paper.pdf total pages: {len(reader_springer.pages)}")
assert len(reader_springer.pages) <= 15

# 4. Update make_springer_proceedings.py
with open(sample_tex, 'r', encoding='utf-8') as f:
    tex_str = f.read()

make_py_path = os.path.join(base_dir, 'make_springer_proceedings.py')
with open(make_py_path, 'w', encoding='utf-8') as f:
    f.write('"""\nmake_springer_proceedings.py\nGenerates samplepaper.tex conforming to the Springer CCIS/LNCS template.\n"""\nimport os\n\n')
    f.write('TEX_CONTENT = r\'\'\'' + tex_str + '\'\'\'\n\n')
    f.write('''def main():
    tex_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'samplepaper.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write(TEX_CONTENT)
    print(f"Successfully generated {tex_path}")

if __name__ == '__main__':
    main()
''')

# 5. Build Overleaf / CMT zip packages
# Package 1: AgentShield_AI_Overleaf_Springer_Package.zip
zip1_path = os.path.join(base_dir, 'AgentShield_AI_Overleaf_Springer_Package.zip')
with zipfile.ZipFile(zip1_path, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write(sample_tex, arcname='samplepaper.tex')
    z.write(os.path.join(base_dir, 'llncs.cls'), arcname='llncs.cls')
    z.write(os.path.join(base_dir, 'splncs04.bst'), arcname='splncs04.bst')
    fig_dir = os.path.join(base_dir, 'paper_figures')
    for f in os.listdir(fig_dir):
        if f.endswith('.png'):
            z.write(os.path.join(fig_dir, f), arcname=os.path.join('paper_figures', f))
print(f"Updated {zip1_path}")

# Package 2: AgentShield_AI_PAUL2026_Revision_Package.zip
zip2_path = os.path.join(base_dir, 'AgentShield_AI_PAUL2026_Revision_Package.zip')
with zipfile.ZipFile(zip2_path, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write(paul_pdf, arcname='AgentShield_AI_PAUL2026_Revised.pdf')
    z.write(sample_tex, arcname='samplepaper.tex')
    resp_pdf = os.path.join(base_dir, 'Response_to_Reviewers_PAUL2026.pdf')
    if os.path.exists(resp_pdf):
        z.write(resp_pdf, arcname='Response_to_Reviewers_PAUL2026.pdf')
    resp_tex = os.path.join(base_dir, 'Response_to_Reviewers_PAUL2026.tex')
    if os.path.exists(resp_tex):
        z.write(resp_tex, arcname='Response_to_Reviewers_PAUL2026.tex')
    z.write(os.path.join(base_dir, 'llncs.cls'), arcname='llncs.cls')
    z.write(os.path.join(base_dir, 'splncs04.bst'), arcname='splncs04.bst')
    fig_dir = os.path.join(base_dir, 'paper_figures')
    for f in os.listdir(fig_dir):
        if f.endswith('.png'):
            z.write(os.path.join(fig_dir, f), arcname=os.path.join('paper_figures', f))
print(f"Updated {zip2_path}")

print("All synchronization and package creation complete!")
