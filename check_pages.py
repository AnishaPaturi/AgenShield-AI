import os
import win32com.client

os.system("taskkill /F /IM WINWORD.EXE /T > nul 2>&1")

try:
    word = win32com.client.Dispatch('Word.Application')
    word.Visible = False
    doc_path = os.path.abspath(r'C:\Users\anish\OneDrive\College\project-clg\AgenShield-AI\AgentShield_AI_Research_Paper_Draft.docx')
    doc = word.Documents.Open(doc_path)
    
    words = doc.ComputeStatistics(0) # 0 = wdStatisticWords
    pages = doc.ComputeStatistics(1) # 1 = wdStatisticPages
    
    doc.Close(False)
    word.Quit()
    
    print(f"WORD_COUNT = {words}")
    print(f"PAGE_COUNT = {pages}")
except Exception as e:
    print(f"COM Error: {e}")
