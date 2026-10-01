import docx

doc = docx.Document("docs/college/PS - Document Format.docx")
for name in ["Normal", "Heading 1", "Heading 2", "Heading 3"]:
    st = doc.styles[name]
    f = st.font
    size_pt = f.size.pt if f.size else "default"
    print(f"{name}: font={f.name}, size={size_pt}pt, bold={f.bold}")

for p in doc.paragraphs[120:130]:
    if p.text.strip():
        for r in p.runs[:2]:
            sz = r.font.size.pt if r.font.size else "style-default"
            print(f"   run: text='{r.text[:30]}', font={r.font.name}, size={sz}")
