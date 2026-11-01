# Reference double-check, 2026-11-01 (main.tex + si.tex)

Second check before the author's own check by hand. 91 cited works, 136 citing sentences.
- Metadata: Crossref comparison by script (`refcheck_2026-11-01/crossref_rows.json`), then resolved by hand.
- Claims: each citing sentence checked against the source by four independent agents (`refcheck_2026-11-01/result1-4.json`).
- All 91 works exist; no retractions. One erratum (liuzza2016), which does not affect the cited values.

| Supported | Partly | Not supported | Unverifiable (full text closed) |
|---|---|---|---|
| 79 | 21 | 1 | 35 |

"Unverifiable" means the number is not in what could be opened (usually the abstract); most rest on the earlier
reading notes only. These are the author's hand-check list (section C).

## A. Claims to fix (source says something different)

| Key | Where | Problem | Suggested fix |
|---|---|---|---|
| rim2010 | introduction l.27 | **Not supported.** Rim & Novoselac never compare near-body sources with sources elsewhere; their occupant-plume source gave no higher exposure than the floor source (the cough-like source did). | Cite rim2010 only for "source location and local airflow govern exposure when mixing is poor"; rest the near-body claim on licina2017. |
| djordjevic2008, dalton1999, herz2001 | results l.178 | "0--3% in intensity": Djordjevic Fig. 1B gives ~1 and ~3 points on a 100-point scale (~5% relative to neutral); Dalton reports a *significant* intensity rise after a "harmful" label (size not in abstract); Herz unverifiable. | e.g. "a few points on a 100-point scale"; check Dalton's effect size; reword the sign clause if Dalton's warned subjects count. |
| cheng2011 | methods l.44 | K lower bound: source gives 0.001, manuscript 10^-4 m^2/s. | 10^-3--1.3x10^-2, or cite a source for 10^-4. |
| amoore1983, wilby1969 | methods l.106 | "10--23 times higher" holds for H2S and methanethiol only; Wilby's DMS (2.0 ppb) is below Nagata's 3.0 ppb; Wilby measured recognition (not detection) thresholds. | Say "for H2S and methanethiol"; SI: "recognition medians" for Wilby. |
| wysocki2006 | breathing (results/SI) | Paper: 10.1 +- 3.0 breaths/min, manuscript 12. Inspiratory fraction 0.42 is right. | Use 10/min, or "12, within the measured 10.1 +- 3.0". |
| fallon2018 | results | Peak intensity 4.85 vs 4.32, p = 0.22, n = 19 (trend lower). | "did not significantly reduce the peak rated intensity". |
| corsetti2017, ronholt1999 | anal relaxation | "19 +- 6 s" not in either source (Ronholt 16--19 s; Corsetti ~24 +- 4 s). | Give the source values, or explain the pooling in the ESM. |
| miller1988b | ESM (2 places) | 0--15 mmHg is the rise when flatus is *sensed*, not passed; passage pressures +8 (-10 to 88) mmHg. | "rising 0--15 mmHg (median 7) when flatus is sensed"; compare with median driving pressure. |
| nagai1993, ng2011 | methods (pressure); ESM | 2.5 kPa is Ng's group mean, not in Nagai (Nagai's lowest 1.1 kPa). | Add ng2011 (and grolman2007) to the methods cite; "on average 2.5 kPa". |
| grolman2007, deschler1999 | methods, ESM l.170 | Tracheo-oesophageal (prosthesis) speakers, not oesophageal speech. | "oesophageal and tracheo-oesophageal phonation". |
| giffard2001 | ESM | 38--86% H2S cut was in faecal incubations, not live dogs. | "in dog faecal incubations ...; fed to dogs, the number of emissions did not change". |
| collins2001 | methods; ESM l.47 | n = 0.28 is from dog flatus, one human judge; the range 0.20--0.45 is not in the source. | Add "dog flatus, one judge"; call 0.20--0.45 an assumed bracket. |
| gibson1993b | ESM | "H2S replaced CH4 almost mole for mole": two subjects; distal matches, proximal does not. | Drop "mole for mole" or give both values. |
| yao2018 | ESM | "up to 50-fold" is FOS vs sterculia, not a rise over baseline (89% and +1557% are right). | "up to 50 times more gas than poorly fermented fibre". |
| hickey1972 | ESM | Tested fruits and juices, not beans/fibre/lactulose. | Add "fruit" to the list of challenges. |
| suarez1998 | introduction | Source: sulphur gases are the major "but not the only" malodorants. | "carry most of it". |
| chapman1967 | discussion | Shows prior word associations create reported co-occurrences; transmission by a phrase alone is our step. | "a prior verbal association alone can produce a reported co-occurrence". |
| li2016 | ESM | Correct for that assay, but Fukutani et al. 2023 (Curr Biol, doi:10.1016/j.cub.2023.04.072) found OR2T11 responds to H2S with copper. | "no response to H2S in that assay", or cite the newer result. |
| calloway1969 | ESM | r = +0.86 only from the 12 control/bean rows; all 22 rows give +0.84. | Say which rows. |
| kepecs2006 | perception | "the unit" slightly stronger than the source ("a unit", mostly rodent data). | "a unit". |

## B. Metadata fixes (refs/references.yaml)

- Missing titles: landeau2014, wysocki2006 (also full author list: Wysocki M, Fiamma MN, Straus C, Poon CS,
  Similowski T), stone1965, dalton1999, hawkins1950 (pages 6--13, issue 1).
- hickey1972: journal in 1972 was *The American Journal of Digestive Diseases*.
- whisman1978: add fourth author Brinkman DW; issue 12.
- hold1977: published as Hold B, Schleidt M (not Hold-Cavell BCL).
- nagai1993: fifth author Ohtsu Y; journal Practica Oto-Rhino-Laryngologica Suppl. 65:164--170.
- liuzza2016: Chem. Senses 42(6):499--508, 2017 (online 2016); erratum doi:10.1093/chemse/bjx001.
- haag2019: print issue 77(11), 2020 (online 2019).
- levine1998: primary DOI 10.1111/j.1572-0241.1998.083_c.x (current one is an alias).
- grose1811: 1811 edition was enlarged after Grose's death (London: C. Chappel); add edition or cite Project
  Gutenberg #5402.
- Minor: suarez1998b third author Springfield J; Lundstrom needs the diacritic; Steggerda co-author Dimmick JF;
  cheng2011 author list confirmed (drop "to be confirmed"); issue numbers missing for several entries.
- Checked and fine: yao2018 pages 510--522 (issue pagination); gibson1993b three authors (Crossref incomplete);
  diez2003 title.
- Style: 15 entries end the author list in "et al." after three names; others list all authors.

## Status (2026-11-01, author's go-ahead): sections A, B and D applied

All fixes below are in the manuscript, ESM and `refs/references.yaml`, with these choices:
- cheng2011: the model keeps K down to 1e-4; the text now says 1e-3 is the lowest measured and the lowest decade is
  assumed (params table: "partly sourced"). wysocki2006: 12/min kept, measured 10.1 +- 3.0 stated.
- suarez1997: the 92-mL median is described as the median of the subjects' mean passage volumes (params table:
  "derived").
- li2016: narrowed to "in that assay". The later contrary result suggested by one agent (Fukutani et al. 2023,
  doi:10.1016/j.cub.2023.04.072) was NOT added: that DOI is a paper on odorant antagonism, not on OR2T11 and H2S.
- Wording was tightened in four places to stay under 8,000 words with references (now about 7,920).

## D. Full-text pass (29 papers supplied by the author, 2026-11-01)

The 29 PDFs are kept locally in `refs/pdfs_incoming/<key>.pdf` (gitignored: the repository is public, so publisher
PDFs are never committed). Keys: amoore1983, cheng2011, corsetti2017, dalton1999, deschler1999, fiorentino2023,
gibson1993, grolman2007, herz2001, hickey1972, kirk1949, levine1998, levitt1976, liuzza2016, marthinsen1982,
miller1988b, ng2011, odonnell1984, pindzola1989, robbins1984, ronholt1999, sangras2002, sorensen2014, steggerda1966,
steggerda1968, suarez1997, tangerman2009, whisman1978, wilby1969.

`refcheck_2026-11-01/handresult1-3.json`; 50 citing sentences: 28 supported, 20 partly, 2 not supported, none still
unverifiable. Section C below is now settled. Findings that change or add to section A:

| Key | Problem (full text) | Suggested fix |
|---|---|---|
| dalton1999 | **Not supported.** "Harmful" label raised rated intensity by 18--61% over a 20-min exposure; "healthful" lowered it 1--8%; all subjects were told something. | Rewrite the results l.178 sentence (with herz2001, djordjevic2008): effects are small for most odours (herz2001 ~2--3%, djordjevic2008 a few points on 100) but large after a harm warning (dalton1999 18--61%); all with the label announced, so the sign for an unwarned listener is not established. |
| herz2001 | Four odours 2.1--2.5% (n.s.), violet leaf 12.5% (p < 0.01); labels announced at every sniff. | As above. |
| sangras2002, diez2003 | Original tables: C_x = 2.6 jet, 8.0 puff (diameter-normalised); Gamma = 2.8 converts from the jet value. C_p = 2.6 in the manuscript's form is in the erratum (diez2003, checked in the first pass). | Cite the constants to the corrected analysis: "Gamma = 2.8 and C_p = 2.6 (corrected analysis \cite{diez2003} of \cite{sangras2002})". |
| kirk1949 | No support for "fermentation fraction rises with output in every study": ordinary diet r = -0.41; after brussels sprouts output rose while the fermentation fraction fell (extra gas mostly N2). | Drop "every study that measured both"; cite Kirk as the exception. |
| whisman1978 | Factor 26 and sigma 3.5 are not in Whisman; they are Amoore's analysis of Whisman's 1977 report. | "(Amoore's analysis \cite{amoore1983} of the tests of \cite{whisman1978})". |
| corsetti2017, ronholt1999 | 19 +- 6 s is Ronholt Table 1 (flatus passage); Corsetti's relaxations 23 +- 4 s. 0--15 mmHg is not in Ronholt (Miller). | "19 +- 6 s \cite{ronholt1999}"; move 0--15 mmHg to miller1988b. |
| miller1988b | 0--15 mmHg (median 7) when flatus is sensed; passing: median 8, range -10 to 88; a third of passages without a rectal rise. | "median rise 8 mmHg (range -10 to 88; 0--15 when only sensed)". |
| suarez1997 | 17--375 mL verbatim; r values exact (Table 3); median 92 mL is not stated (median of the 16 subjects' mean passage volumes, from Table 1); the production/consumption mechanism in the discussion is our inference. | "median 92 mL (of the subjects' mean passage volumes, from \cite{suarez1997})"; mark the mechanism as ours. |
| hickey1972 | Fruits and juices only; r = +0.857 from Table 2 (rounds to the stated lower bound). | "bean, fibre, fruit and lactulose challenges". |
| levine1998 | r = 0.112 is H2S release vs CH4 release of incubated faeces, not faecal sulfide in producers vs non-producers. | Keep strocchi1991/florin1991 for "did not differ"; cite levine1998 for the non-correlation. |
| cheng2011 | Lowest K in the paper 1.07e-3 m2/s; nothing near 1e-4. | 1e-3--1.3e-2, or justify 1e-4 separately as still air. |
| wilby1969 | Recognition medians (panel of 35): 4.1, 0.80, 2.0 ppb; DMS below Nagata. | "10--23 times higher for H2S and methanethiol"; ESM: recognition medians. |
| tangerman2009 | Composition exact (Table 2); thresholds are the lowest in Verschueren's handbook, not "the literature". | Name the source. |
| fiorentino2023 | Office confirmed; the high case pairs OH (30 Oct) and O3 (31 Oct) from different days. | Say so, or use the same-day pair (OH 9.8e5, O3 1.5 ppb). |
| ng2011 | 2.46 kPa is a group mean of peak pressure in speech; individuals 1.0--3.0 kPa. | "about 2.5 kPa on average (1.0--3.0)". |
| grolman2007, deschler1999 | Tracheo-oesophageal speakers (Grolman 1.8/2.2/5.1 kPa; Deschler F0 82--116 Hz). | "oesophageal and tracheo-oesophageal". |
| gibson1993 | Review; supports the sulphate-reducing route only. | Leave cysteine/gene prevalence to braccia2021. |

Confirmed: levitt1976 (26 to 79%, r = +0.98), steggerda1966 (r = +0.98), steggerda1968 (+0.94; the earlier +0.999 was CO2
alone), odonnell1984 (+0.94), marthinsen1982 (+0.880 from diet means), liuzza2016, pindzola1989, robbins1984,
sorensen2014, amoore1983 (20x and 23x; factor 26, sigma 3.5), tangerman2009 free sulfide < 5% (H2S only).
Metadata: ronholt1999 pages 1551--1559; grolman2007 Tan FML; levitt1976 Schwartz JS; steggerda1966 Dimmick JF;
whisman1978 add Brinkman DW; liuzza2016 final pagination (Chem. Senses 42(6):499--508); sangras2002 issue 3.

## C. Hand-check list (full text closed; numbers rest on reading notes) — settled by section D

Highest weight first:
1. **suarez1997** (8 sentences): 17--375 mL (median 92); r = +0.56, -0.50, |r| <= 0.22, n = 87; sulphur concentration vs
   volume. The abstract links fast CO2/H2 production to passage rate, not volume.
2. **tangerman2009** (4 sentences): 28 passages; H2S 149, CH3SH 216, DMS 144 nmol/L; thresholds compilation; free
   sulfide < 5% (Table 2).
3. **fiorentino2023** (3): OH 9.8x10^5 cm^-3, O3 0.7--2.6 ppb, "office" (abstract says "a room").
4. **herz2001**, **dalton1999**: label effect sizes (see A).
5. **sangras2002 / diez2003**: confirm C = 2.8 for the starting jet and 2.6 for the puff are not swapped (the
   erratum gives exactly these).
6. levitt1976 (26% at 55 mL to 79% at 720 mL per 4 h, Table 1); liuzza2016 (2.51 vs 3.71, Table 4); levine1998
   (Fig. 3, r = 0.112); steggerda1968 (+0.999 from Table 1 vs "+0.86 to +0.99"); marthinsen1982 (r = +0.88,
   Table 4); hickey1972 and odonnell1984 (r values); kirk1949, steggerda1966, sorensen2014, robbins1984,
   pindzola1989, grolman2007, whisman1978 (factor 26, sigma 3.5), gibson1993.
7. ~~hirani2009: the scene in *3 Idiots* where the silent release is called the deadliest.~~ Confirmed by the author
   (2026-11-01); sentence kept.
