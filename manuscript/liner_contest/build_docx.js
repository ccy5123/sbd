// Build the contest draft as a Word file from draft_ko.md (the Markdown stays the source of truth).
// Format after the contest guideline docx: A4, Batang, body 10 pt; title, chapter and section headings in bold;
// tables with a shaded header row; references with a hanging indent. [ ] placeholders are highlighted yellow.
// Usage (needs the npm package docx): node build_docx.js [draft_ko.md] [out.docx]
const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, AlignmentType,
  BorderStyle, Header, Footer, PageNumber, HeadingLevel,
} = require("docx");

const src = process.argv[2] || path.join(__dirname, "draft_ko.md");
const out = process.argv[3] || path.join(__dirname, "draft_ko.docx");
const FONT = "Batang";
const PT = (p) => p * 2;               // docx sizes are half-points
const CONTENT_W = 11906 - 2 * 1418;    // A4 width minus 25 mm margins, DXA

// inline Markdown: **bold**, *italic*, [placeholder] -> runs
function runs(text, base = {}) {
  const out = [];
  const re = /(\*\*[^*]+\*\*|\*[^*]+\*|\[[^\]]*\])/g;
  let last = 0, m;
  const push = (t, o = {}) => t && out.push(new TextRun({ text: t, font: FONT, size: PT(10), ...base, ...o }));
  while ((m = re.exec(text))) {
    push(text.slice(last, m.index));
    const t = m[0];
    if (t.startsWith("**")) push(t.slice(2, -2), { bold: true });
    else if (t.startsWith("*")) push(t.slice(1, -1), { italics: true });
    else push(t, { highlight: "yellow" });
    last = m.index + t.length;
  }
  push(text.slice(last));
  return out;
}

const para = (text, opts = {}, runOpts = {}) =>
  new Paragraph({ children: runs(text, runOpts), spacing: { line: 384, after: 120 }, alignment: AlignmentType.JUSTIFIED, ...opts });

function table(rows) {
  const cells = rows.map((r) => r.replace(/^\||\|$/g, "").split("|").map((c) => c.trim()));
  const n = cells[0].length;
  // column weight: longest body cell, header counted at half (headers may wrap), numbers kept narrow
  const len = (j) => Math.max(cells[0][j].length / 2, ...cells.slice(1).map((r) => (r[j] || "").length));
  const weights = [...Array(n).keys()].map((j) => Math.max(6, Math.min(len(j), 36)));
  const total = weights.reduce((a, b) => a + b, 0);
  const widths = weights.map((w) => Math.floor((CONTENT_W * w) / total));
  widths[n - 1] += CONTENT_W - widths.reduce((a, b) => a + b, 0);
  const border = { style: BorderStyle.SINGLE, size: 4, color: "808080" };
  const borders = { top: border, bottom: border, left: border, right: border };
  return new Table({
    width: { size: CONTENT_W, type: WidthType.DXA },
    columnWidths: widths,
    rows: cells.map((r, i) => new TableRow({
      tableHeader: i === 0,
      children: r.map((c, j) => new TableCell({
        width: { size: widths[j], type: WidthType.DXA },
        borders,
        shading: i === 0 ? { type: ShadingType.CLEAR, color: "auto", fill: "E7E6E6" } : undefined,
        margins: { top: 60, bottom: 60, left: 80, right: 80 },
        children: [new Paragraph({ children: runs(c, { size: PT(9), bold: i === 0 }),
                                   alignment: j === 0 || isNaN(parseFloat(c)) ? AlignmentType.LEFT : AlignmentType.CENTER })],
      })),
    })),
  });
}

let md = fs.readFileSync(src, "utf8").replace(/<!--[\s\S]*?-->/g, "");
const lines = md.split(/\r?\n/);
const body = [];
let inRefs = false;
for (let i = 0; i < lines.length; i++) {
  const l = lines[i];
  if (!l.trim()) continue;
  if (l.startsWith("# ")) {
    body.push(new Paragraph({ children: runs(l.slice(2), { size: PT(18), bold: true }), alignment: AlignmentType.CENTER,
                              spacing: { before: 240, after: 200, line: 360 } }));
  } else if (l.startsWith("## ")) {
    const t = l.slice(3);
    inRefs = t === "참고문헌";
    body.push(new Paragraph({ heading: HeadingLevel.HEADING_1, children: runs(t, { size: PT(14), bold: true, color: "000000" }),
                              spacing: { before: 360, after: 160 } }));
  } else if (l.startsWith("### ")) {
    body.push(new Paragraph({ heading: HeadingLevel.HEADING_2, children: runs(l.slice(4), { size: PT(12), bold: true, color: "000000" }),
                              spacing: { before: 240, after: 120 } }));
  } else if (l.startsWith("|")) {
    const rows = [];
    while (i < lines.length && lines[i].startsWith("|")) {
      if (!/^\|[-| ]+\|$/.test(lines[i].trim())) rows.push(lines[i]);
      i++;
    }
    i--;
    body.push(table(rows));
    body.push(new Paragraph({ children: [], spacing: { after: 120 } }));
  } else if (l.startsWith("- ") && inRefs) {
    body.push(para(l.slice(2), { indent: { left: 567, hanging: 567 }, alignment: AlignmentType.LEFT,
                                spacing: { line: 300, after: 80 } }, { size: PT(9) }));
  } else if (/^\*\*표 \d+\.\*\*/.test(l)) {
    body.push(para(l, { alignment: AlignmentType.LEFT, keepNext: true, spacing: { before: 120, after: 80 } }, { size: PT(9) }));
  } else if (/^\[그림 \d/.test(l)) {
    body.push(para(l, { alignment: AlignmentType.CENTER, spacing: { before: 120, after: 160 } }, { size: PT(9) }));
  } else if (i < 6 && !l.startsWith("#")) {
    body.push(para(l, { alignment: AlignmentType.CENTER, spacing: { after: 240 } }));   // name and date line
  } else {
    body.push(para(l, { indent: { firstLine: 200 } }));
  }
}

const doc = new Document({
  creator: "", title: lines.find((x) => x.startsWith("# ")).slice(2),
  styles: { default: { document: { run: { font: FONT, size: PT(10) } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1418, bottom: 1418, left: 1418, right: 1418 } } },
    headers: { default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT,
      children: [new TextRun({ text: "제1회 라이너 스콜라 연구공모전", font: FONT, size: PT(8), color: "7F7F7F" })] })] }) },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER,
      children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: PT(8) })] })] }) },
    children: body,
  }],
});
Packer.toBuffer(doc).then((b) => { fs.writeFileSync(out, b); console.log("wrote", out); });
