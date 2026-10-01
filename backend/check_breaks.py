import docx

doc = docx.Document('docs/college/PS - Document Format_backup.docx')
p289 = doc.paragraphs[289]
print("p289 XML:")
print(p289._p.xml)
