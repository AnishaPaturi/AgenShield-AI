import sys
sys.stdout.reconfigure(encoding='utf-8')
import docx

doc = docx.Document('docs/college/PS - Document Format.docx')
print("--- PARAGRAPHS 200 TO 288 ---")
for i in range(200, min(290, len(doc.paragraphs))):
    txt = doc.paragraphs[i].text.strip()
    if txt:
        print(f"[{i}] {txt}")
