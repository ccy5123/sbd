"""Character count of the contest draft: main text from the abstract through the conclusion, spaces included,
Markdown markup and HTML comments removed (the contest asks for about 10,000 characters excluding references).
Usage: python count_chars.py [draft_ko.md]"""
import re
import sys

text = open(sys.argv[1] if len(sys.argv) > 1 else "draft_ko.md", encoding="utf-8").read()
body = text.split("## 초록", 1)[1].split("## 참고문헌", 1)[0]
body = re.sub(r"<!--.*?-->", "", body, flags=re.S)
body = re.sub(r"^#+ ", "", body, flags=re.M)
body = re.sub(r"\*\*|\*|\|", "", body)
body = re.sub(r"^-+$|^[-| ]+$", "", body, flags=re.M)
lines = [l.strip() for l in body.splitlines() if l.strip()]
joined = "\n".join(lines)
print(f"main text: {len(joined.replace(chr(10), ''))} characters with spaces, {len(re.sub(r'\s', '', joined))} without")
for sec in re.split(r"\n(?=제\d장|제\d절)", "초록\n" + joined):
    print(f"  {sec.splitlines()[0][:30]:32s} {len(sec.replace(chr(10), ''))}")
