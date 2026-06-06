# Context Handoff — Tandayapa AudioMoth Project (v2, current state)

Use this file to continue the project in a new chat without losing context. It reflects the **current, deployed design** and supersedes the earlier handoff.

---

## 1. Project at a glance

- **Course:** acoustic ecology field research, Tandayapa Cloud Forest Station, Ecuador.
- **Group:** Franz Chandi, Maria Andrade, Priscila Cajas, Noemi Castro.
- **Equipment:** 6 AudioMoth recorders (3 forest, 3 pasture).
- **Type of study:** methodological — about recorder spacing and spatial independence, NOT an edge-gradient study.
- **Goal:** help other researchers decide how far apart to place acoustic recorders so samples are independent (avoid spatial pseudoreplication).

---

## 2. What was actually deployed in the field (IMPORTANT — this is final)

- 3 AudioMoths in **forest**, placed ~**20 m inside the forest edge**, spread across the patch.
- 3 AudioMoths in **pasture**, open grazing land near the same edge.
- Recorders are **NOT paired** and **NOT in straight lines**. Placement was **opportunistic** (terrain + safety), not a designed grid.
- Note: 2 of the forest recorders happened to fall on a roughly **perpendicular line to the edge** — this was not by design and is acknowledged as a limitation (possible small edge gradient).
- ~20 m forest depth was chosen because deeper access is steep/unsafe and often needs a cut path.

### The key methodological reframe (this is the heart of the project)
Because recorders are not paired or lined up, the design does **NOT** use fixed distance categories (no 15/30/45 m treatments). Instead it uses the **actual straight-line GPS distance between every pair of recorders as a continuous predictor**. With 3 recorders per habitat → **3 pairwise comparisons per habitat**, each at its own real distance. This turns the opportunistic placement into a legitimate continuous distance-decay design.

---

## 3. Research question (English + Spanish)

**EN:** How does the similarity of sound recorded by two AudioMoths change with the distance between them, and is this distance–similarity relationship different in forest than in pasture? Measured using ACI, BI, and ADI.

**ES:** ¿Cómo cambia la similitud del sonido grabado por dos AudioMoth con la distancia entre ellos, y esta relación distancia–similitud es diferente en el bosque que en el pastizal? Medido con ACI, BI y ADI.

**Methodological benefit (the "sell"):** most acoustic surveys guess at recorder spacing. This gives a field-based starting point for spacing recorders far enough apart to count as independent samples, and the workflow transfers to any soundscape project.

---

## 4. Hypothesis + predictions

**Hypothesis (EN):** Two recorders record less similar sound as the distance between them grows (distance decay). Because forest vegetation and terrain absorb/scatter sound more than open pasture, each forest recorder "hears" a smaller area, so similarity should drop over **shorter distances in forest than in pasture**.

**Predictions:**
- **P1:** Pairwise difference in ACI/BI/ADI increases with distance between recorders.
- **P2 (key):** That increase is **steeper in forest than in pasture**.
- **P3:** Pattern is clearest during high-activity hours (dawn/dusk choruses).

**Phrasing rule:** always say recordings become *more different* / *less similar* with distance. NEVER say "the indices increase with distance."

---

## 5. Variables, sampling unit, replication

- **Dependent variable (Y):** pairwise acoustic dissimilarity between two recorders = absolute difference in an index, e.g. `abs(ACI_1 - ACI_2)`, computed per hour. One model per index (ACI, BI, ADI).
- **Independent variables (X):** distance between pair (continuous, metres); habitat (forest/pasture); distance × habitat interaction (tests whether the decay slope differs).
- **Sampling units:** recorder = spatial unit of the soundscape; recorder **pair** = unit of the distance analysis; 10-min clips & hours = **temporal subsamples**, summarized to hourly, never treated as independent.
- **Replication:** 3 array points per habitat = spatial replicates; repeated days/hours enter the model as random effects.

---

## 6. Statistical model (final, in R)

```r
library(lme4)
library(lmerTest)   # adds p-values

# scale distance to help convergence / interpretability
d$distance_z <- scale(d$distance)

m <- lmer(dissimilarity ~ distance_z * habitat + (1 | pair) + (1 | day),
          data = d)
summary(m)
```

- `distance_z * habitat` → main effects + the **distance:habitat interaction** (the key test for P2: significant interaction = different decay rate in forest vs pasture).
- `(1 | pair)` → random intercept; same pair measured repeatedly over time.
- `(1 | day)` → random intercept; absorbs day-to-day weather/activity.

**Optional upgrade (random slope), if data allow convergence:**
```r
m2 <- lmer(dissimilarity ~ distance_z * habitat + (1 | pair) + (1 + distance_z | day),
           data = d)
```
With few days/pairs this may fail to converge → fall back to `m`.

**Rigorous backup for shared-recorder non-independence:** Mantel / MRM test on distance matrices (`vegan` / `ecodist`).

**Possible alternative if dissimilarity is bounded/skewed:** `glmmTMB` with an appropriate family (e.g. Gamma or Beta). Not yet written — open task.

---

## 7. Limitations (already on the slides)

1. Only 3 recorders/habitat → few pairwise distances, low power. It's a pilot / proof-of-method, not a definitive threshold.
2. Placement opportunistic, not randomized → habitat and location effects can partly mix.
3. Two forest recorders fell ~perpendicular to the edge → possible small edge gradient mixed with distance.
4. Pairwise comparisons share recorders → not fully independent (handled by random effects / Mantel).
5. Acoustic indices respond to rain, wind, water, human noise; don't directly measure richness/abundance.
6. "Forest" = near-edge forest (~20 m), not deep interior.

---

## 8. Deliverables already produced (in this project)

1. **`Tandayapa_acoustic_spacing_proposal.docx`** — full written proposal (study area, question+hypothesis EN/ES, field methodology, design methodology, statistics, limitations). NOTE: this docx was written around an *earlier* design that used unequal spacing (0/15/45 m) and rotating arrays; the user later clarified the recorders were placed opportunistically (not in lines). The **slides + scripts are the up-to-date version**; the docx may need updating to match the final non-lined design.
2. **`Tandayapa_acoustic_presentation.pptx`** — 12-slide deck, English, forest-green theme, ~15 min. Reflects the FINAL design. Slide order: (1) title, (2) problem/pseudoreplication, (3) study area, (4) research question + payoff, (5) hypothesis + predictions, (6) field methodology, (7) design methodology + expected-pattern chart, (8) variables & sampling unit, (9) R model, (10) limitations, (11) why it helps researchers, (12) conclusion + next steps.
3. **Four speaker scripts** (markdown), English to read aloud + Spanish to understand, 3 slides each:
   - `Script_1_Franz_intro_and_study_area.md` (slides 1–3)
   - `Script_2_Maria_question_and_field.md` (slides 4–6)
   - `Script_3_Priscila_design_and_statistics.md` (slides 7–9, technical)
   - `Script_4_Noemi_limitations_and_conclusion.md` (slides 10–12, close)

Design/theme details for consistency: palette = Forest & Moss (forest `2C5F2D`, dark `1E4220`, moss `97BC62`, cream `F7F8F3`); pasture accent = gold `D9A441`; header font Georgia, body Calibri, code Consolas; soundwave motif on title/closing slides.

---

## 9. Open questions / next tasks for the new chat

The user has NOT yet provided:
- **How many days** the recorders stay deployed.
- **Actual pairwise distances** between recorders (from GPS).

When those arrive, the new chat should:
1. Put the real distances into slide 7's expected-pattern chart and into the model example.
2. Optionally write the `glmmTMB` version of the model (bounded/skewed dissimilarity).
3. Possibly update `Tandayapa_acoustic_spacing_proposal.docx` to match the final opportunistic (non-lined) design.
4. Help with the actual analysis once recordings are downloaded (compute ACI/BI/ADI per hour, build the pairwise dissimilarity table, fit the model, compare forest vs pasture slopes, validate with manual sound labels).

---

## 10. Key things the new chat must remember

- Final design = 3 forest + 3 pasture, **opportunistic placement, not paired, not in lines**, forest ~20 m inside edge.
- Distance is **continuous (GPS), not categorical**. No 15/30/45 m treatments.
- Y = pairwise dissimilarity (difference between two recorders' index values), per hour.
- The **distance × habitat interaction** is the central hypothesis test (P2).
- Repeated clips/hours = temporal subsamples, summarized, not independent replicates.
- Indices: ACI, BI, ADI. Manual labels = supporting validation only, not part of the indices.
- Slides + scripts are the current source of truth; the docx is slightly behind.
- Honest framing of limitations (small n, pilot study) is a strength — keep it.
