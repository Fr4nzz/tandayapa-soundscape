# Context Handoff — Tandayapa AudioMoth Spacing Project (CURRENT)

Self-contained handoff so a new Claude chat can continue cold. This reflects the
**final, deployed design** and supersedes any earlier handoff (v1 edge-gradient and the
0/15/45 m "lined array" ideas are obsolete — do not use them).

Last updated: 2026-06-03.

---

## 1. Project at a glance

- **Course:** acoustic ecology field research, Tandayapa Cloud Forest Station, Ecuador.
- **Group:** Franz Chandi, Maria Andrade, Priscila Cajas, Noemi Castro.
- **Equipment:** 6 AudioMoth recorders (3 forest + 3 pasture).
- **Study type:** methodological — about **recorder spacing and spatial independence of acoustic samples**, NOT an edge-gradient study, NOT a habitat-comparison study per se.
- **Practical payoff ("the sell"):** most acoustic surveys guess how far apart to place recorders. This gives a field-based starting point for spacing recorders far enough that samples count as independent (avoid spatial pseudoreplication). The workflow transfers to any soundscape project.

---

## 2. Final field design (this is what was actually deployed — do not change)

- 3 AudioMoths in **forest**, ~**20 m inside the forest edge**, spread across the patch.
  (~20 m chosen because deeper access is steep/unsafe and often needs a cut path.)
- 3 AudioMoths in **pasture**, open grazing land near the same edge.
- Placement is **opportunistic** (terrain + safety), **NOT paired**, **NOT in straight lines**, NOT a designed grid.
- Known quirk: 2 forest recorders happened to fall ~perpendicular to the edge → acknowledged as a limitation (possible small edge gradient mixed into distance).

### The key methodological reframe (heart of the project)
Because recorders are not paired or lined up, the design uses the **actual straight-line GPS
distance between each pair of recorders as a continuous predictor** — NOT fixed distance
categories (no 15/30/45 m treatments). With 3 recorders per habitat → **3 within-habitat
pairwise comparisons per habitat**, each at its own real distance. Opportunistic placement
becomes a legitimate continuous distance-decay design.

---

## 3. Research question

**EN:** How does the similarity of sound recorded by two AudioMoths change with the distance
between them, and is this distance–similarity relationship different in forest than in pasture?
Measured using ACI, BI, and ADI.

**ES:** ¿Cómo cambia la similitud del sonido grabado por dos AudioMoth con la distancia entre
ellos, y esta relación distancia–similitud es diferente en el bosque que en el pastizal?
Medido con ACI, BI y ADI.

---

## 4. Hypothesis + predictions

**Hypothesis (EN):** Two recorders record less similar sound as the distance between them grows
(distance decay). Because forest vegetation and terrain absorb/scatter sound more than open
pasture, each forest recorder "hears" a smaller area, so similarity should drop over **shorter
distances in forest than in pasture**.

**Hypothesis (ES):** Dos grabadoras registran sonido menos similar a medida que aumenta la
distancia entre ellas (decaimiento con la distancia). Como la vegetación y el terreno del bosque
absorben/dispersan más el sonido que el pastizal abierto, cada grabadora de bosque "escucha" un
área menor, por lo que la similitud debería caer a **distancias más cortas en el bosque que en el
pastizal**.

**Predictions:**
- **P1:** Pairwise difference in ACI/BI/ADI increases with distance between recorders.
- **P2 (key test):** That increase is **steeper in forest than in pasture**.
- **P3:** Pattern is clearest during high-activity hours (dawn/dusk choruses).

### Phrasing rules (important)
- SAY: "recordings become more different", "differences between index values increase",
  "sound information becomes less similar".
- NEVER say: "the indices increase with distance" / "ACI/BI/ADI increase with distance" /
  "abundance increases with distance".

---

## 5. Variables, sampling unit, replication

- **Response (Y):** pairwise acoustic dissimilarity between two recorders = absolute difference
  in an index, e.g. `abs(ACI_1 - ACI_2)`, computed per hour. **One model per index** (ACI, BI, ADI).
- **Predictors (X):** distance between the pair (continuous, metres); habitat (forest/pasture);
  **distance × habitat interaction** (tests whether the decay slope differs — this is P2).
- **Sampling units:** recorder = spatial unit of the soundscape; recorder **pair** = unit of the
  distance analysis; 10-min clips & hours = **temporal subsamples**, summarized to hourly, NEVER
  treated as independent replicates.
- **Replication:** 3 array points per habitat = spatial replicates; repeated days/hours enter the
  model as random effects.

---

## 6. Statistical model (final, R)

```r
library(lme4)
library(lmerTest)   # adds p-values

d$distance_z <- scale(d$distance)   # scale distance for convergence / interpretability

m <- lmer(dissimilarity ~ distance_z * habitat + (1 | pair) + (1 | day),
          data = d)
summary(m)
```

- `distance_z * habitat` → main effects + the **distance:habitat interaction** (significant
  interaction = different decay rate in forest vs pasture = support for P2).
- `(1 | pair)` → same pair measured repeatedly over time.
- `(1 | day)` → absorbs day-to-day weather/activity.

**Optional random-slope upgrade (if it converges):**
```r
m2 <- lmer(dissimilarity ~ distance_z * habitat + (1 | pair) + (1 + distance_z | day), data = d)
```
With few days/pairs this may not converge → fall back to `m`.

**Backup for shared-recorder non-independence:** Mantel / MRM test on distance matrices
(`vegan` / `ecodist`).

**If dissimilarity is bounded/skewed:** `glmmTMB` with Gamma or Beta family (not yet written).

---

## 7. Analysis pipeline (once recordings are downloaded)

1. Compute ACI, BI, ADI per recorder per hour (R packages `soundecology` and/or `seewave`).
2. Build the **pairwise table**: for each within-habitat recorder pair, for each hour, compute
   `dissimilarity = abs(index_i - index_j)` and attach `distance` (GPS), `habitat`, `pair`, `day`, `hour`.
3. Fit one mixed model per index (section 6); inspect the distance×habitat interaction.
4. Plot: X = pairwise distance, Y = pairwise dissimilarity, separate lines/points for forest vs pasture.
5. Use **manual sound labels** (birds, insects, amphibians, rain, wind, water, human noise) to
   interpret/validate what drives index differences. Manual labels are supporting validation only —
   they are NOT inside the indices.

---

## 8. Limitations (honest framing is a strength — keep it)

1. Only 3 recorders/habitat → few pairwise distances, low power. It's a **pilot / proof-of-method**, not a definitive spacing threshold.
2. Placement opportunistic, not randomized → habitat and location effects can partly mix.
3. Two forest recorders ~perpendicular to edge → possible small edge gradient mixed with distance.
4. Pairwise comparisons share recorders → not fully independent (handled by random effects / Mantel).
5. Acoustic indices respond to rain, wind, water, human noise; they don't directly measure richness/abundance.
6. "Forest" = near-edge forest (~20 m), not deep interior.

---

## 9. Deliverables status

Existing files in this repo (`/home/franz/Tandayapa-field-research/`):
- `deliverables/Tandayapa_field_research_acoustic_short_proposal.docx` — **OLD design** (edge-gradient).
- `deliverables/Tandayapa_acoustic_project_slides.pptx` — **OLD design**.
- `scripts/build_acoustic_project_slides.py`, `scripts/build_short_edge_gradient_docx.py` — generators for the old versions.

Files referenced in the prior v2 handoff but **NOT present in this repo** (they live in another chat/export):
- `Tandayapa_acoustic_spacing_proposal.docx` (final-ish proposal; may still describe a lined 0/15/45 design — needs updating to the opportunistic non-lined design).
- `Tandayapa_acoustic_presentation.pptx` (12-slide deck, English, forest-green theme; reflects the final design).
- 4 speaker scripts (markdown), English to read + Spanish to understand, 3 slides each:
  `Script_1_Franz_intro_and_study_area.md` (1–3), `Script_2_Maria_question_and_field.md` (4–6),
  `Script_3_Priscila_design_and_statistics.md` (7–9), `Script_4_Noemi_limitations_and_conclusion.md` (10–12).

Slide deck design/theme (for consistency): palette **Forest & Moss** (forest `2C5F2D`, dark
`1E4220`, moss `97BC62`, cream `F7F8F3`); pasture accent gold `D9A441`; header Georgia, body
Calibri, code Consolas; soundwave motif on title/closing slides. 12-slide order: (1) title,
(2) problem/pseudoreplication, (3) study area, (4) question + payoff, (5) hypothesis + predictions,
(6) field methodology, (7) design methodology + expected-pattern chart, (8) variables & sampling
unit, (9) R model, (10) limitations, (11) why it helps researchers, (12) conclusion + next steps.

---

## 10. Missing inputs (needed to finish)

The group has NOT yet provided:
- **How many days** the recorders stayed deployed.
- **Actual pairwise GPS distances** between recorders (per habitat).

When those arrive: put the real distances into the slide-7 expected-pattern chart and into the
model example; then run the real analysis (section 7).

---

## 11. Candidate next tasks for the new chat

1. Update the proposal `.docx` to match the final opportunistic (non-lined, non-paired) design.
2. Insert real GPS distances into the slide-7 chart + model example (once provided).
3. Write the `glmmTMB` (Gamma/Beta) version of the model for bounded/skewed dissimilarity.
4. Build the analysis pipeline end-to-end (compute ACI/BI/ADI per hour → pairwise table → fit
   models → forest-vs-pasture slope comparison → validate with manual labels).

---

## 12. Hard rules the new chat must remember

1. Final design = 3 forest + 3 pasture, **opportunistic, not paired, not in lines**, forest ~20 m inside edge.
2. Distance is **continuous (GPS), not categorical**. No 15/30/45 m treatments.
3. Y = pairwise dissimilarity (`abs(index_i - index_j)`), per hour, one model per index.
4. The **distance × habitat interaction** is the central hypothesis test (P2).
5. Repeated clips/hours = temporal subsamples, summarized, never independent replicates.
6. Indices: ACI, BI, ADI. Manual labels = supporting validation only, not part of the indices.
7. Never say indices increase with distance — say recordings become more different / less similar.
8. Only 3 recorders/habitat → low power → it's a pilot; keep the honest limitations.
9. The repo's `.docx`/`.pptx` are on the OLD design; the final design lives in this handoff.
