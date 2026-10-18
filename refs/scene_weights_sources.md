# Scene weights for the headline (HANDOFF item 3) — sources, 2026-10-18

Definition (user's choice): weight of scene k ∝ time per day an adult spends close (≈0.5–1.5 m) to another person
in that setting; passages uniform over waking hours. DOIs verified via OpenAlex; "seen" = number read in the source.
Not yet approved by the user; not yet in params.yaml.

## Sofa (side by side at home)
- TV with others present 52.4 % of 2 h 46 min (US 15+, ATUS 2013–17): Krantz-Kent 2018, BLS Beyond the Numbers 7(14),
  Chart 3, https://www.bls.gov/opub/btn/volume-7/television-capturing-americas-attention.htm (seen). "Others" = in
  the same room (ATUS technical note, https://www.bls.gov/news.release/atus.tn.htm, seen).
- TV 2.61 h/day, socializing 0.58 h/day, 2025: ATUS Table 11A, https://www.bls.gov/news.release/atus.t11A.htm (seen).
- → 2.61 × 0.524 ≈ 1.4 h/day (range 0.8–2.0: adults only / plus seated socializing).

## Elevator
- Mean in-car time 24 s; 32.1 % of trips shared (COVID rules, so low); 69.7 % shared among regular users:
  Robal et al. 2022, Balt J Mod Comput 10(4), 10.22364/bjmc.2022.10.4.05, p. 678, Table 2 (seen).
- Lobby group size 1.2–1.3 (office): Sorsa et al. 2020, BSERT, 10.1177/0143624420983974 (abstract, seen).
- Trips per passenger: "4 trips per day, 250 days per year"; 18 billion US trips/yr (≈0.15 per resident per day):
  NEII fact sheet (grey literature, data mostly 2007),
  https://nationalelevatorindustry.org/wp-content/uploads/2019/02/Fact-Sheet.pdf (seen). No peer-reviewed rate found.
- → office worker ≈0.01 h/day (range 0.0005 population average – 0.1 high-rise resident and worker, assumption).

## Standing pair talking (no direct measurement found)
- Time talking 23.2–39.7 % of waking samples (least vs happiest; n = 79): Mehl et al. 2010, Psychol Sci 21(4):539,
  10.1177/0956797610362675 (seen). ~16 000 words/day: Mehl et al. 2007, Science 317:82, 10.1126/science.1139940.
- Standing 4.1 h of 14.7 h awake-and-measured (office workers, activPAL): Smith et al. 2015, BMC Public Health,
  10.1186/s12889-014-1338-1; 21–32 % standing: Johansson et al. 2020, BMC Public Health 20:826,
  10.1186/s12889-020-08909-w.
- → [ASSUMPTION] 0.5 h/day (range 0.2–1.5; floor from ATUS socializing 0.58 h/day × ~½ standing).

## Proposed weights (sofa / elevator / standing)
| case | h/day | weight |
|---|---|---|
| central | 1.4 / 0.01 / 0.5 | 0.73 / 0.005 / 0.26 |
| home-centred | 2.0 / 0.0005 / 0.2 | 0.91 / 0.0002 / 0.09 |
| office, high-rise | 0.8 / 0.1 / 1.5 | 0.33 / 0.04 / 0.63 |

Caveats: the elevator weight is ≤ 4 % in every case; the result hinges on the sofa/standing split, whose standing
side is an assumption, so report the range. ATUS is US only. Unchecked lead: Siikonen 2021, People Flow in
Buildings ch. 4, 10.1002/9781119545590.ch4 (may hold per-person trip rates).
