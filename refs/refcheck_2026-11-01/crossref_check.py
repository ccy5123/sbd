"""Compare every cited reference (main.aux + si.aux) with Crossref metadata; also dump citation contexts.
Usage: python crossref_check.py <repo_root> <out_dir>"""
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
from difflib import SequenceMatcher
from pathlib import Path

import yaml

root, out = Path(sys.argv[1]), Path(sys.argv[2])
pre = root / "manuscript/preprint"
refs = yaml.safe_load((root / "refs/references.yaml").read_text(encoding="utf-8"))["references"]


def keys(aux):
    ks = set()
    for m in re.finditer(r"\\citation\{([^}]*)\}", (pre / aux).read_text(encoding="utf-8", errors="replace")):
        ks.update(k.strip() for k in m.group(1).split(","))
    return ks


main_k, si_k = keys("main.aux"), keys("si.aux")
cited = sorted(main_k | si_k)


def norm(s):
    s = unicodedata.normalize("NFKD", str(s or "")).encode("ascii", "ignore").decode().lower()
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def sim(a, b):
    return SequenceMatcher(None, norm(a), norm(b)).ratio()


def crossref(doi):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/")
    req = urllib.request.Request(url, headers={"User-Agent": "refcheck/1.0 (mailto:noreply@example.org)"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)["message"]
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}


rows = []
for k in cited:
    e = refs.get(k)
    row = {"key": k, "in": "+".join(x for x, s in (("main", main_k), ("si", si_k)) if k in s)}
    if e is None:
        row["status"] = "MISSING_IN_YAML"
        rows.append(row)
        continue
    row["entry"] = e
    doi = e.get("doi")
    if not doi:
        row["status"] = "NO_DOI"
        rows.append(row)
        continue
    m = crossref(str(doi))
    time.sleep(0.2)
    if "error" in m:
        row["status"] = "DOI_ERROR"
        row["error"] = m["error"]
        rows.append(row)
        continue
    cr_title = (m.get("title") or [""])[0]
    cr_auth = [a.get("family", a.get("name", "")) for a in m.get("author", [])]
    cr_year = None
    for f in ("published-print", "published-online", "issued"):
        if m.get(f, {}).get("date-parts"):
            cr_year = m[f]["date-parts"][0][0]
            break
    years = {m[f]["date-parts"][0][0] for f in ("published-print", "published-online", "issued")
             if m.get(f, {}).get("date-parts") and m[f]["date-parts"][0][0]}
    cr_jour = (m.get("container-title") or [""])[0]
    first = norm(str(e.get("authors", [""])[0]).split()[0]) if e.get("authors") else ""
    issues = []
    if e.get("title") and sim(e["title"], cr_title) < 0.85:
        issues.append(f"title: yaml={e['title']!r} | crossref={cr_title!r}")
    if not e.get("title"):
        issues.append(f"title missing in yaml; crossref={cr_title!r}")
    if first and cr_auth and first not in norm(cr_auth[0]) and norm(cr_auth[0]) not in first:
        issues.append(f"first author: yaml={e['authors'][0]!r} | crossref={cr_auth[0]!r}")
    n_yaml = len([a for a in e.get("authors", []) if "et al" not in str(a)])
    if e.get("authors") and "et al" not in " ".join(map(str, e["authors"])) and cr_auth and n_yaml != len(cr_auth):
        issues.append(f"author count: yaml={n_yaml} | crossref={len(cr_auth)} {cr_auth}")
    if e.get("year") and int(e["year"]) not in years:
        issues.append(f"year: yaml={e['year']} | crossref={sorted(years)}")
    if e.get("journal") and cr_jour and sim(e["journal"], cr_jour) < 0.6 and norm(e["journal"]) not in norm(cr_jour):
        issues.append(f"journal: yaml={e['journal']!r} | crossref={cr_jour!r}")
    if e.get("volume") and m.get("volume") and str(e["volume"]) != str(m["volume"]):
        issues.append(f"volume: yaml={e['volume']} | crossref={m['volume']}")
    if e.get("pages") and m.get("page"):
        p_y = re.split(r"[-–]", str(e["pages"]))[0].strip().lstrip("e")
        p_c = re.split(r"[-–]", str(m["page"]))[0].strip().lstrip("e")
        if p_y != p_c:
            issues.append(f"pages: yaml={e['pages']} | crossref={m['page']}")
    if m.get("relation", {}).get("is-retracted-by") or "retract" in norm(cr_title):
        issues.append("RETRACTION flag")
    if any(u.get("update-type") in ("retraction", "correction", "expression_of_concern")
           for u in m.get("update-to", [])):
        issues.append("update-to: " + str(m["update-to"]))
    row.update(status="ISSUES" if issues else "OK", issues=issues,
               crossref={"title": cr_title, "authors": cr_auth, "year": cr_year, "journal": cr_jour,
                         "volume": m.get("volume"), "page": m.get("page"), "type": m.get("type")})
    rows.append(row)

(out / "crossref_rows.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False, default=str), encoding="utf-8")
for r in rows:
    if r["status"] != "OK":
        print(f"[{r['status']}] {r['key']} ({r['in']})")
        for i in r.get("issues", []):
            print("    ", i)
        if r["status"] == "NO_DOI":
            print("    ", {k: v for k, v in r["entry"].items() if k in ("authors", "editors", "organization", "year",
                                                                        "title", "journal", "publisher", "url")})
print("cited:", len(cited), "OK:", sum(r["status"] == "OK" for r in rows))

# citation contexts: the sentence around each \cite in main sections and si.tex
texts = {f"main/{p.name}": p for p in sorted((pre / "sections").glob("*.tex"))}
texts["si.tex"] = pre / "si.tex"
ctx = {k: [] for k in cited}
for name, p in texts.items():
    t = p.read_text(encoding="utf-8", errors="replace")
    for m in re.finditer(r"\\cite[pt]?\*?(?:\[[^\]]*\])*\{([^}]*)\}", t):
        a = max(t.rfind(". ", 0, m.start()), t.rfind("\n\n", 0, m.start()), m.start() - 600)
        b_candidates = [x for x in (t.find(". ", m.end()), t.find("\n\n", m.end())) if x != -1]
        b = min(b_candidates + [m.end() + 400])
        s = re.sub(r"\s+", " ", t[a + 1:b + 1]).strip()
        for k in (x.strip() for x in m.group(1).split(",")):
            if k in ctx:
                ctx[k].append(f"[{name}] {s}")
(out / "contexts.json").write_text(json.dumps(ctx, indent=1, ensure_ascii=False), encoding="utf-8")
print("keys with no context found:", [k for k, v in ctx.items() if not v])
