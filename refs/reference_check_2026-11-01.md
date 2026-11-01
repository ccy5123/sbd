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

## C. Hand-check list (full text closed; numbers rest on reading notes)

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
