"""Build the LaTeX source package of the manuscript for EPJ Plus (Editorial Manager compiles it itself).

Editorial Manager wants one flat folder (no subfolders) with the source, every figure and the compiled PDF; the ESM is
uploaded separately as a PDF (Online Resource 1, ESM_1.pdf). So main.tex is made standalone:
  * every \\input is inlined;
  * the ESM cross-references (\\ref{SI-...}, package xr) are replaced by their numbers read from si.aux, and the xr
    lines are dropped;
  * the bibliography is pasted in from main.bbl (no BibTeX run needed);
  * figures are copied next to main.tex and \\graphicspath points there.
Output: manuscript/preprint/submission/latex/ (main.tex, main.pdf, figures, README.txt) and
manuscript/preprint/submission/ESM_1.pdf. Run from the repository root after building si.pdf and main.pdf (needs
si.aux and main.bbl): python3 manuscript/preprint/make_latex_package.py
"""
import re
import shutil
from pathlib import Path

PRE = Path(__file__).resolve().parent
FIG_DIRS = [PRE / "figs", PRE.parents[1] / "figures"]  # same search order as \graphicspath in the sources
OUT = PRE / "submission" / "latex"
INPUT = re.compile(r"^(?P<pre>[^%\n]*?)\\input\{(?P<name>[^}]+)\}", re.M)
GRAPHICS = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
SI_REF = re.compile(r"\\ref\{SI-([^}]+)\}")
NEWLABEL = re.compile(r"\\newlabel\{([^}]+)\}\{\{([^}]*)\}")


def flatten(path: Path) -> str:
    text = path.read_text(encoding="utf-8")

    def inline(m):
        name = m.group("name")
        sub = PRE / (name if name.endswith(".tex") else name + ".tex")
        return f"{m.group('pre')}% ---- begin {name}.tex ----\n{flatten(sub).rstrip()}\n% ---- end {name}.tex ----"

    return INPUT.sub(inline, text)


def si_labels() -> dict:
    return {m.group(1): m.group(2) for m in NEWLABEL.finditer((PRE / "si.aux").read_text(encoding="utf-8"))}


def find_figure(name: str) -> Path:
    for d in FIG_DIRS:
        for cand in (d / name, *(d / (name + ext) for ext in (".pdf", ".png", ".jpg"))):
            if cand.is_file():
                return cand
    raise FileNotFoundError(name)


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    tex = flatten(PRE / "main.tex")
    labels = si_labels()
    missing = sorted({k for k in SI_REF.findall(tex) if k not in labels})
    assert not missing, f"ESM labels not in si.aux: {missing}"
    tex = SI_REF.sub(lambda m: labels[m.group(1)], tex)
    tex = re.sub(r"^\\usepackage\{xr\}[^\n]*\n", "", tex, flags=re.M)
    tex = re.sub(r"^\\externaldocument[^\n]*\n", "", tex, flags=re.M)
    bbl = (PRE / "main.bbl").read_text(encoding="utf-8")
    tex, n = re.subn(r"\\bibliographystyle\{[^}]*\}\s*\\bibliography\{[^}]*\}", lambda m: bbl.strip(), tex)
    assert n == 1, "bibliography commands not found"
    tex = re.sub(r"\\graphicspath\{.*\}[^\n]*", r"\\graphicspath{{./}}", tex)
    for name in GRAPHICS.findall(tex):
        src = find_figure(name)
        shutil.copy2(src, OUT / src.name)
    (OUT / "main.tex").write_text(tex, encoding="utf-8")
    shutil.copy2(PRE / "main.pdf", OUT / "main.pdf")
    shutil.copy2(PRE / "si.pdf", PRE / "submission" / "ESM_1.pdf")
    (OUT / "README.txt").write_text(
        "LaTeX source of the manuscript. main.tex is standalone: the bibliography is included and the numbers of the\n"
        "sections, figures and tables of Online Resource 1 (ESM_1.pdf, uploaded separately) are written in.\n"
        "Build: pdflatex main.tex (twice). Standard packages only (article class, natbib, siunitx, mhchem, lineno).\n",
        encoding="utf-8")
    figs = [p.name for p in OUT.iterdir() if p.suffix in (".png", ".pdf", ".jpg") and p.name != "main.pdf"]
    print(f"{OUT}: main.tex (standalone), main.pdf, {len(figs)} figures; ESM_1.pdf")


if __name__ == "__main__":
    main()
