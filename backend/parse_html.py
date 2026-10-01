import re

with open("docs/college/index.html", "r", encoding="utf-8") as f:
    html = f.read()

# Find all headings or slide markers
titles = re.findall(r'<h[1-4][^>]*>(.*?)</h[1-4]>', html, re.DOTALL)
print("Found headings in index.html:")
for i, t in enumerate(titles):
    clean_t = re.sub(r'<[^>]+>', '', t).strip()
    if clean_t:
        print(f"{i+1}: {clean_t}")
