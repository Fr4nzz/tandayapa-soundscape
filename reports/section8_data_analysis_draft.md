# 8. Data Analysis  *(draft for the shared Word — ready to paste)*

All recordings were two-minute WAV files (48 kHz). We analysed the data along two
complementary lines: (a) classifier-free **acoustic indices**, and (b) the **species community**
detected by an automated classifier. Throughout, we report **effect sizes** — the size and
direction of each relationship together with a 95% confidence interval — rather than relying on
p-values alone, because for a small pilot study the magnitude of an effect is more informative than
statistical significance by itself.

**Acoustic indices.** For each recording we computed three standard soundscape indices with the
scikit-maad library (Ulloa et al., 2021): the Acoustic Complexity Index (ACI), the Bioacoustic Index
(BI, 2–8 kHz), and the Acoustic Diversity Index (ADI, up to 10 kHz). We averaged the indices over a
representative sample of recordings to obtain one ACI, BI, and ADI value per recorder, and also one
value per time-of-day period (dawn, day, dusk, night) for the diel comparison.

**Distance and habitat.** To test whether the distance between recorders changes the acoustic
information they capture, we compared every pair of recorders deployed in the **same habitat on the
same day**. For each pair we calculated the absolute difference in each index (|ΔACI|, |ΔBI|,
|ΔADI|) and the inter-recorder distance. Because each transect had three points (1–2–3), every
deployment produced pairs separated by one spacing and by two spacings; across all deployments the
realised distances were **15, 30, 60, and 120 m**. We modelled the index difference as a function of
distance, separately for forest and pasture, and tested whether that relationship differed between
habitats (a distance × habitat interaction).

**Species community (BirdNET).** In parallel we used BirdNET (Kahl et al., 2021) to detect birds and
insects, and a complementary classifier for frogs, in every recording. After expert review we
removed three frog taxa identified as false positives, and kept detections above a confidence
threshold of **0.5** (we repeated the analysis at 0.25 and 0.7 to confirm the conclusions did not
depend on this choice). For each recorder we built a species-by-activity table and, for each
within-habitat recorder pair, computed two community-dissimilarity measures: **Bray–Curtis** (from
detection counts) and **Jaccard** (from presence/absence). This lets us ask the same distance
question in terms of **biodiversity (species turnover)** and compare whether the cheap acoustic
indices capture the same spatial pattern as the species data.

**Accounting for the sampling design.** Because the three recorders on a transect shared points (the
same point was reused across distance treatments; see Limitations), the recorder pairs within a
deployment are **not fully independent**. To account for this, all analyses used **linear mixed
models with the deployment day as a random intercept**, so that each replicate day has its own
baseline and the distance effect is estimated *within* the replication structure rather than from
pseudo-replicated pairs. Each spacing (15, 30, 60 m) was deployed on **two separate days**, providing
replicate blocks (Sugai et al., 2019; Bradfer-Lawrence et al., 2023).

**Effect sizes reported.** For each index and for community dissimilarity we report the **slope with
distance (change per +10 m), its 95% confidence interval, and the variance explained (R²)**; a
confidence interval that does not include zero indicates a distance effect. The habitat comparison
is reported as the **difference between the forest and pasture slopes** with its 95% confidence
interval.

**Diel comparison.** To examine acoustic activity across the day, we compared ACI, BI, and ADI among
**dawn, day, dusk, and night** in each habitat.

**Software.** Acoustic indices and detections were produced in Python (scikit-maad; BirdNET);
community metrics and mixed models were computed in R (`vegan` for dissimilarities; `lme4`/`lmerTest`
for the mixed models; `ggplot2` for figures). The full analysis is reproducible from an R Markdown
report.

---

### References to add (for the ones not already in the list)

- Ulloa, J. S., Haupert, S., Latorre, J. F., Aubin, T., & Sueur, J. (2021). scikit-maad: An open-source and modular toolbox for quantitative soundscape analysis in Python. *Methods in Ecology and Evolution*, 12(12), 2334–2340.
- Kahl, S., Wood, C. M., Eibl, M., & Klinck, H. (2021). BirdNET: A deep learning solution for avian diversity monitoring. *Ecological Informatics*, 61, 101236.
- Oksanen, J., et al. (2024). *vegan: Community Ecology Package*. R package.
- Bates, D., Mächler, M., Bolker, B., & Walker, S. (2015). Fitting linear mixed-effects models using lme4. *Journal of Statistical Software*, 67(1), 1–48.
