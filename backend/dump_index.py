import re
import sys

with open("docs/college/index.html", "r", encoding="utf-8") as f:
    text = f.read()

clean = re.sub(r'<style.*?</style>', '', text, flags=re.DOTALL)
clean = re.sub(r'<script.*?</script>', '', clean, flags=re.DOTALL)
clean = re.sub(r'<[^>]+>', ' ', clean)
lines = [l.strip() for l in clean.splitlines() if l.strip()]

with open("backend/index_text.txt", "w", encoding="utf-8") as out:
    for i, l in enumerate(lines):
        out.write(f"{i}: {l}\n")

print("Wrote", len(lines), "lines to backend/index_text.txt")
