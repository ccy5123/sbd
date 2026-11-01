"""Build a self-contained LaTeX source package of the manuscript and the ESM for journal upload.

Output: manuscript/preprint/submission/latex/ with main.tex and si.tex (every \\input inlined), refs.bib (only the
cited entries), main.bbl and si.bbl, and figures/ (only the images used). Build si.tex first, then main.tex: main.tex
reads si.aux for the S-numbers. Run from the repository root after building main.pdf and si.pdf (needs main.aux,
si.aux and the two .bbl files): python3 manuscript/preprint/make_latex_package.py
"""
import re
import shutil
from pathlib import Path

PRE = Path(__file__).resolve().parent
FIG_DIRS = [PRE / "figs", PRE.parents[1] / "figures"]  # same search order as \graphicspath in the sources
OUT = PRE / "submission" / "latex"
INPUT = re.compile(r"^(?P<pre>[^%\n]*?)\\input\{(?P<name>[^}]+)\}", re.M)
GRAPHICS = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")


def flatten(path: Path) -> str:
    text = path.read_text(encoding="utf-8")

    def inline(m):
        name = m.group("name")
        sub = PRE / (name if name.endswith(".tex") else name + ".tex")
        return f"{m.group('pre')}% ---- begin {name}.tex ----\n{flatten(sub).rstrip()}\n% ---- end {name}.tex ----"

    return INPUT.sub(inline, text)


def cited_keys(aux: Path) -> set[str]:
    keys = set()
    for m in re.finditer(r"\\citation\{([^}]*)\}", aux.read_text(encoding="utf-8", errors="replace")):
        keys.update(k.strip() for k in m.group(1).split(","))
    return keys


def bib_subset(keys: set[str]) -> str:
    text = (PRE / "refs.bib").read_text(encoding="utf-8")
    entries = re.split(r"\n(?=@)", text)
    keep = [e.strip() for e in entries if (m := re.match(r"@\w+\{([^,]+),", e.strip())) and m.group(1) in keys]
    missing = keys - {re.match(r"@\w+\{([^,]+),", e).group(1) for e in keep}
    assert not missing, f"cited but not in refs.bib: {sorted(missing)}"
    return "% Cited entries of refs.bib (generated from refs/references.yaml).\n\n" + "\n\n".join(keep) + "\n"


def find_figure(name: str) -> Path:
    for d in FIG_DIRS:
        for cand in (d / name, *(d / (name + ext) for ext in (".pdf", ".png", ".jpg"))):
            if cand.is_file():
                return cand
    raise FileNotFoundError(name)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "figures").mkdir(parents=True)
    keys = set()
    for stem in ("si", "main"):
        tex = flatten(PRE / f"{stem}.tex")
        tex = re.sub(r"\\graphicspath\{.*\}[^\n]*", r"\\graphicspath{{figures/}}", tex)
        for name in GRAPHICS.findall(tex):
            src = find_figure(name)
            shutil.copy2(src, OUT / "figures" / src.name)
        (OUT / f"{stem}.tex").write_text(tex, encoding="utf-8")
        shutil.copy2(PRE / f"{stem}.bbl", OUT / f"{stem}.bbl")
        keys |= cited_keys(PRE / f"{stem}.aux")
    (OUT / "refs.bib").write_text(bib_subset(keys), encoding="utf-8")
    (OUT / "README.txt").write_text(
        "LaTeX source of the manuscript (main.tex) and the electronic supplementary material (si.tex).\n"
        "Build order: pdflatex si, bibtex si, pdflatex si (x2); then pdflatex main, bibtex main, pdflatex main (x2).\n"
        "main.tex reads si.aux (package xr) for the numbers of ESM sections, figures and tables.\n"
        "Or: latexmk -pdf si.tex && latexmk -pdf main.tex\n", encoding="utf-8")
    print(f"{OUT}: main.tex, si.tex, refs.bib ({len(keys)} cited), .bbl, "
          f"{len(list((OUT / 'figures').iterdir()))} figures")


if __name__ == "__main__":
    main()
