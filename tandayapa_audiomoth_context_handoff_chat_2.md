# Context Handoff: Tandayapa AudioMoth Field Research Project

This file summarizes the full discussion so a new chat can continue the project without losing context. It includes the user’s main queries, design changes, ideas considered, current decisions, and points that still need refinement.

---

## 1. Project background

The project is for a field research class in acoustic ecology at **Tandayapa Cloud Forest Station, Ecuador**.

The group is working with **AudioMoth acoustic recorders** to design a short, feasible, methodological field project. The study must be realistic for a short field course with limited time, difficult terrain, and limited equipment.

Main constraints discussed:

- Forest access is difficult, steep, and sometimes unsafe.
- It is hard to create long transects inside the forest because paths may need to be made manually.
- The group initially had **4 AudioMoths**, later updated this to **6 AudioMoths**.
- The group wants a design that is simple, defensible, and methodologically focused.
- Repeated recordings should be treated as **temporal subsamples**, not independent spatial replicates.
- AudioMoth settings, height, orientation, recording schedule, and clip duration should be standardized.

---

## 2. Files uploaded during the discussion

### Uploaded proposal document

File: `Tandayapa_field_research_acoustic_short_proposal.docx`

This contained the original edge-gradient proposal.

Original research question:

> How does biological acoustic complexity change with distance from the forest edge in naturally restored and riparian forests at Tandayapa Cloud Forest Station, and does this edge-gradient pattern vary by time of day?

Original design idea:

- Compare naturally restored forest and riparian forest.
- Use four AudioMoth positions along an edge-to-interior gradient:
  - Outside forest
  - Forest edge
  - Intermediate point
  - Interior point
- Sample three transects per forest type.
- Summarize repeated 10-minute recordings by hour.
- Calculate acoustic indices:
  - Acoustic Complexity Index (ACI)
  - Bioacoustic Index (BI)
  - Acoustic Diversity Index (ADI)
- Use manual listening/spectrogram review to classify broad sound categories:
  - Birds
  - Insects
  - Amphibians
  - Abiotic sounds
  - Human noise

### Uploaded slide deck

File: `Tandayapa_acoustic_project_slides.pptx`

The slides originally described the edge-gradient design. They were updated once to include the newer methodological idea, but the user later corrected that the design should **not be paired between forest and pasture**.

---

## 3. Sequence of user queries and design changes

### Query 1: Original problem with forest access and ecological succession gradient

The user explained that the group originally wanted to do a forest field research experiment, but entering the forest was difficult because the group had to make its own path, and the terrain was steep and dangerous.

Because of this, the group considered switching to an ecological succession/restoration gradient using four AudioMoths:

1. Pasture
2. Planted *Alnus* trees in pasture
3. Denser *Alnus* patch with wild naranjilla, around 2.5–3 m tall
4. A forest point about 50 m inside the forest

The teacher said the design needed replication. The group realized the ideal design would require more replicates per gradient step, which was difficult.

An alternative idea considered was testing whether two close AudioMoths, for example 10–20 m apart, record similar results compared with two AudioMoths at the same distance but in different habitats.

This led to the idea of comparing:

- Less restored habitat
- More restored habitat
- Whether distance or habitat explains similarity between recordings

### Query 2: Changed research question to distance between AudioMoths

The user then changed the research question:

> We want to see at which distance the AudioMoths detect significantly different distances and does habitat type affect that. We are going to study pasture and forest, get in the forest like 20 m inside, and put AudioMoths at different distances parallel to the forest edge.

Important design point introduced:

- In the forest, place AudioMoths about **20 m inside the forest**.
- In pasture, place AudioMoths also at a standardized distance from the edge.
- Place AudioMoths **parallel to the forest edge** so that distance from the edge is not confounded with distance between recorders.

Suggested early distances included:

- 0, 20, 40, 60 m
- Alternative if space is limited: 0, 15, 30, 45 m

The logic was to ask whether acoustic information changes with distance between AudioMoths and whether this pattern differs between forest and pasture.

### Query 3: More specific methodological distance question

The user then clarified:

> We changed our research question now we want to find the minimum distance at which AudioMoth results are different in two habitats, forest and pasture, which might be paired.

The group was thinking:

- Put AudioMoths around 20 m from the edge inside the forest.
- Place 3 AudioMoths inside the forest separated by a fixed distance parallel to the edge.
- One day could use 15 m spacing.
- Another day could use 25 m spacing.
- Another day could use 50 m spacing.
- Expect that in forest, differences may be found faster at smaller distances than in pasture.

The recommended research question at that stage was:

> How does acoustic dissimilarity between AudioMoth recordings change with distance in forest and pasture habitats, and at what tested distance do recordings begin to differ within each habitat?

But the user later said that **“acoustic dissimilarity” sounds difficult** and wanted simpler wording.

### Query 4: The group now has 6 AudioMoths

The user corrected that the group now has **6 AudioMoths**, not 4.

This allowed a stronger simultaneous design:

- 3 AudioMoths in forest
- 3 AudioMoths in pasture

Earlier suggestion:

- Use pairwise distances like 15 m, 30 m, and 45 m within each habitat.
- Example layout:
  - F1–F2 = 15 m
  - F2–F3 = 30 m
  - F1–F3 = 45 m
- Same idea for pasture.

However, this design was later corrected by the user because the group decided **not to necessarily pair forest and pasture**.

### Query 5: Make the research question easier to explain

The user wanted the question to be easier to explain and avoid difficult wording like “acoustic dissimilarity.”

The user also wanted the question to include metrics:

- Acoustic indices
- Manually labeled sound detections
- Possibly detection abundance by broad taxa/groups

A simpler methodological framing was proposed:

> We want to know how far apart AudioMoths need to be before they stop recording almost the same sound information, and whether this distance is different in forest and pasture.

A simple research question accepted by the user:

> How far apart do AudioMoths need to be to record different sound information in forest and pasture habitats near a forest edge?

Later, the user wanted to add metrics to the question.

### Query 6: Add acoustic indices and manual labels

The user liked the question:

> How far apart do AudioMoths need to be to record different sound information in forest and pasture habitats near a forest edge?

Then the user asked to add:

- Acoustic indices
- Manually labeled sound detections

A proposed version was:

> How far apart do AudioMoths need to be to record different sound information in forest and pasture habitats near a forest edge, based on acoustic indices and manually labeled sound detections?

Then the user translated it into Spanish:

> A que distancia los audiomoths capturan diferente informacion de sonidos en el bosque y pastizal en base a indices acusticos y sonidos manualmente etiquetados

A more polished Spanish version was:

> ¿A qué distancia las grabadoras AudioMoth comienzan a capturar información sonora diferente en bosque y pastizal, según índices acústicos y detecciones sonoras etiquetadas manualmente?

### Query 7: Simplify to indices only

The user then clarified:

> The manual labels should already be in the indices so we should simplify the question to straight say indices but mention which indices we are going to use.

Important clarification:

- Manual labels are **not actually inside the indices**.
- Acoustic indices are calculated automatically from the recordings.
- Manual labels should be treated as **supporting validation or interpretation**, not part of the main research question unless desired.

Simplified Spanish research question suggested:

> ¿A qué distancia los AudioMoth registran información sonora diferente en bosque y pastizal, según los índices acústicos ACI, BI y ADI?

More formal version:

> ¿A qué distancia las grabadoras AudioMoth comienzan a capturar información sonora diferente en bosque y pastizal, evaluada mediante el Índice de Complejidad Acústica (ACI), el Índice Bioacústico (BI) y el Índice de Diversidad Acústica (ADI)?

### Query 8: Need Pregunta + Hypothesis, field methodology, design methodology, limitations

The user requested:

- Pregunta + Hypothesis
- Metodología campo
- Methodology de diseño
- Limitations
- In English and Spanish

A bilingual draft was created with:

Research question:

> At what distance do AudioMoth recorders begin to capture different sound information in forest and pasture habitats near a forest edge, based on the Acoustic Complexity Index (ACI), Bioacoustic Index (BI), and Acoustic Diversity Index (ADI)?

Hypothesis:

> AudioMoth recorders placed farther apart will capture more different sound information. We expect this difference to appear at shorter distances in the forest than in the pasture because forest vegetation, habitat structure, and terrain may reduce sound transmission and create more localized soundscapes.

Important later correction from the user:

- The indices will **not necessarily increase with distance**.
- The study should not say the index values themselves increase.
- Instead, the **difference between recordings/index values** may increase with distance, or recordings may become more different with distance.
- The study is about when AudioMoths capture different sound information, not about assuming ACI, BI, or ADI increase.

### Query 9: Update slides

The user uploaded `Tandayapa_acoustic_project_slides.pptx` and asked to update slides to include:

- Pregunta + Hypothesis
- Field methodology
- Design methodology
- Limitations
- Study area

A new slide deck was generated:

File generated: `Tandayapa_acoustic_project_slides_updated.pptx`

However, the user later corrected the design assumptions:

- The group will **not do a paired forest–pasture design**.
- There is no reason to pair forest and pasture directly.
- The indices will not necessarily increase with distance.
- The group will test AudioMoth spacing using three distances:
  - 15 m
  - 30 m
  - 45 m
- The AudioMoths will be left for **2 days at the same distance**.
- After 2 days, the group may move them to **three different points**, not reuse the same points.
- Whether using different points is best is debatable and should be discussed.

---

## 4. Current best understanding of the project

The current project is a **methodological acoustic monitoring study**.

The main idea is:

> Determine how far apart AudioMoths need to be placed before their recordings provide different sound information, and compare that pattern between forest and pasture.

The study is **not primarily** asking whether forest and pasture have different acoustic indices.

The study is **not primarily** an edge-gradient study anymore.

The study is about **recorder spacing** and **sample independence** in two habitat types.

---

## 5. Current preferred research question

### Spanish

> ¿A qué distancia los AudioMoth registran información sonora diferente en bosque y pastizal, según los índices acústicos ACI, BI y ADI?

### More formal Spanish

> ¿A qué distancia las grabadoras AudioMoth comienzan a registrar información sonora diferente en bosque y pastizal, evaluada mediante el Índice de Complejidad Acústica (ACI), el Índice Bioacústico (BI) y el Índice de Diversidad Acústica (ADI)?

### English

> At what distance do AudioMoth recorders begin to record different sound information in forest and pasture habitats, based on the Acoustic Complexity Index (ACI), Bioacoustic Index (BI), and Acoustic Diversity Index (ADI)?

### Simpler English

> How far apart do AudioMoths need to be to record different sound information in forest and pasture, based on ACI, BI, and ADI?

---

## 6. Current hypothesis — corrected version

The hypothesis should **not** say that the acoustic indices will increase with distance.

Better hypothesis:

### English

> AudioMoth recordings will become more different from each other as the distance between recorders increases. This difference may appear at shorter distances in forest than in pasture because forest vegetation, terrain, and habitat structure can reduce sound transmission and create more localized sound conditions.

### Spanish

> Las grabaciones de los AudioMoth serán más diferentes entre sí a medida que aumente la distancia entre grabadoras. Esta diferencia podría aparecer a distancias más cortas en el bosque que en el pastizal, debido a que la vegetación, el terreno y la estructura del hábitat del bosque pueden reducir la transmisión del sonido y generar condiciones sonoras más localizadas.

### Important phrasing

Use:

- “recordings become more different”
- “differences between index values increase”
- “sound information becomes less similar”

Avoid:

- “indices increase with distance”
- “ACI/BI/ADI increase with distance”
- “abundance increases with distance”

---

## 7. Metrics

The main acoustic indices are:

1. **ACI — Acoustic Complexity Index**
   - Measures rapid changes in sound intensity across frequency bands.
   - Often used as a proxy for biological acoustic activity, but can be affected by noise.

2. **BI — Bioacoustic Index**
   - Measures sound energy in frequency ranges often used by animals.
   - Can reflect overall biological sound activity.

3. **ADI — Acoustic Diversity Index**
   - Measures how evenly sound energy is distributed across frequency bands.
   - Can indicate broader soundscape structure.

Manual labels:

- Manual labels should be used as **validation/supporting interpretation**.
- They can help determine if index differences are due to:
  - Birds
  - Insects
  - Amphibians
  - Rain
  - Wind
  - Water/stream noise
  - Human noise

Do not claim manual labels are “inside” the indices. Better wording:

> Manual sound labeling will be used to interpret and validate the acoustic indices.

---

## 8. Current field design idea

### Equipment

- 6 AudioMoths

### Habitats

- Forest
- Pasture

### Placement relative to edge

- Forest AudioMoths should be approximately **20 m inside the forest**.
- Pasture AudioMoths should be placed within pasture, ideally at a standardized distance from the forest edge.
- AudioMoths should be placed **parallel to the forest edge** to avoid mixing edge distance with recorder spacing.

### Spacing treatments

The group decided to test three distances:

- 15 m
- 30 m
- 45 m

### Current deployment idea

The user said:

- Leave the AudioMoths for **2 days at the same distance**.
- After 2 days, move them to **3 different points**.
- They will **not necessarily use the same points**.
- The design is debatable: using the same points controls for location but risks site-specific effects; using different points increases spatial coverage but adds site variability.

---

## 9. Not paired forest–pasture

Important correction:

The user said:

> We will not do paired; there is no reason to pair forest and pasture.

Therefore, future drafts/slides should avoid saying:

- “paired forest–pasture design”
- “paired AudioMoths between habitats”
- “forest and pasture sampled as matched pairs”

Better wording:

> Forest and pasture will be sampled as separate habitat treatments using the same spacing distances and standardized recorder settings.

Or:

> The same spacing treatments will be applied independently in forest and pasture.

---

## 10. Possible design options to discuss in the new chat

The user wants to continue in a new chat, so the new chat should help decide between these design options.

### Option A: Same points across all distances

Use the same general sites/lines for 15 m, 30 m, and 45 m spacing.

Pros:

- Better controls for site differences.
- Easier to compare distances.
- More internally consistent.

Cons:

- The same site may influence the results strongly.
- Moving AudioMoths along the same line may create logistical issues.
- Reusing the same area may not represent the habitat broadly.

### Option B: New points for each distance

Use new points/lines after 2 days at each distance.

Pros:

- Better spatial coverage.
- Reduces the chance that results are only from one unusual location.
- May be easier if terrain or access changes.

Cons:

- Distance treatment becomes confounded with site if each distance is measured in different places.
- Differences might be caused by location, not spacing.
- Needs careful interpretation.

### Option C: Compromise design

Use multiple independent lines/blocks, and within each block test a spacing treatment. If possible, repeat each distance in more than one location.

Example:

- 2 days at 15 m in one forest line and one pasture line
- 2 days at 30 m in a different but comparable forest line and pasture line
- 2 days at 45 m in another comparable forest line and pasture line

Interpret cautiously:

> Differences among distances may include both spacing effects and site effects, because each distance may be sampled in different points.

### Option D: Rotating distances across comparable blocks

If enough field days and safe sites exist, rotate distances across habitat blocks.

Example:

- Block 1: forest and pasture tested at 15 m
- Block 2: forest and pasture tested at 30 m
- Block 3: forest and pasture tested at 45 m
- Repeat if possible.

This is stronger but may be too complex for a short field course.

---

## 11. Suggested slide outline for the corrected version

The slide deck should be updated again using the corrected design.

### Slide 1: Title and study area

Title:

> Testing AudioMoth spacing in forest and pasture habitats near a cloud-forest edge

Include:

- Tandayapa Cloud Forest Station, Ecuador
- Acoustic ecology / methodological study
- Group members
- Study area:
  - Forest habitat
  - Pasture habitat
  - Sites near forest edge
  - AudioMoths placed parallel to edge

### Slide 2: Research question and hypothesis

Research question:

> At what distance do AudioMoth recorders begin to record different sound information in forest and pasture habitats, based on ACI, BI, and ADI?

Hypothesis:

> Recordings from AudioMoths placed farther apart will become more different from each other. This difference may appear at shorter distances in forest than in pasture because forest vegetation and terrain can reduce sound transmission and create more localized sound conditions.

### Slide 3: Field methodology

Include:

- 6 AudioMoths
- Two habitat types:
  - Forest
  - Pasture
- Forest recorders placed about 20 m inside the forest.
- Pasture recorders placed in open pasture near the forest edge.
- Recorders placed parallel to the forest edge.
- Test spacing distances:
  - 15 m
  - 30 m
  - 45 m
- Each spacing distance will be sampled for 2 days.
- AudioMoths will be moved to new points after each 2-day sampling period, unless the group decides to reuse points.

### Slide 4: Design methodology

Include:

- Methodological goal:
  - Evaluate recorder spacing and independence of acoustic samples.
- Habitat treatments:
  - Forest
  - Pasture
- Spacing treatments:
  - 15 m
  - 30 m
  - 45 m
- Response variables:
  - Difference in ACI between recorders
  - Difference in BI between recorders
  - Difference in ADI between recorders
- Manual labels:
  - Used to interpret and validate whether index differences are due to birds, insects, amphibians, abiotic noise, or human noise.
- Repeated clips summarized by hour.

### Slide 5: Analysis idea

Main comparison:

> Do recordings become more different as distance between AudioMoths increases?

Second comparison:

> Does this pattern differ between forest and pasture?

Graph:

- X-axis: spacing distance, 15/30/45 m
- Y-axis: difference between recorder index values
- Separate points/lines for forest and pasture

Important:

- The analysis compares **differences between recorders**, not whether the indices themselves increase with distance.

### Slide 6: Limitations

Include:

- The study tests only three distances: 15, 30, and 45 m.
- It cannot identify the exact universal minimum distance for all AudioMoth studies.
- If each distance uses different points, distance effects may be partly confounded with site effects.
- Weather, rain, wind, insects, water noise, and human noise can affect acoustic indices.
- Terrain and vegetation may make placement imperfect.
- Acoustic indices do not directly measure species richness or abundance.
- Manual labels help interpretation but do not fully remove uncertainty.

---

## 12. Key corrections the next chat must remember

1. The project is now methodological, focused on AudioMoth spacing.
2. The study is no longer an edge-gradient study.
3. The group now has 6 AudioMoths.
4. The group will test 3 spacing distances:
   - 15 m
   - 30 m
   - 45 m
5. The group plans to leave AudioMoths for 2 days at the same distance.
6. After 2 days, the group may move them to new points.
7. The design should not be described as paired between forest and pasture.
8. Do not say indices increase with distance.
9. Say recordings or index differences become more different with distance.
10. Acoustic indices:
    - ACI
    - BI
    - ADI
11. Manual labels are supporting validation/interpretation, not part of the indices.
12. Forest AudioMoths should be about 20 m inside the forest.
13. Recorders should be placed parallel to the forest edge.
14. Repeated clips should be summarized by hour, not treated as independent replicates.
15. Limitations must mention that using new points for each distance may confound spacing with site.

---

## 13. Possible final wording for the next proposal draft

### English

**Research question**  
At what distance do AudioMoth recorders begin to record different sound information in forest and pasture habitats, based on the Acoustic Complexity Index (ACI), Bioacoustic Index (BI), and Acoustic Diversity Index (ADI)?

**Hypothesis**  
Recordings from AudioMoths placed farther apart will become more different from each other. This difference may appear at shorter distances in forest than in pasture because forest vegetation, terrain, and habitat structure can reduce sound transmission and create more localized sound conditions.

**Methodological focus**  
This study evaluates how recorder spacing affects the independence of acoustic samples. By testing 15 m, 30 m, and 45 m spacing in forest and pasture habitats, we aim to identify the distance at which AudioMoths begin to capture different sound information under local field conditions.

### Spanish

**Pregunta de investigación**  
¿A qué distancia los AudioMoth registran información sonora diferente en bosque y pastizal, según el Índice de Complejidad Acústica (ACI), el Índice Bioacústico (BI) y el Índice de Diversidad Acústica (ADI)?

**Hipótesis**  
Las grabaciones de AudioMoth colocados a mayor distancia serán más diferentes entre sí. Esta diferencia podría aparecer a distancias más cortas en el bosque que en el pastizal, debido a que la vegetación, el terreno y la estructura del hábitat del bosque pueden reducir la transmisión del sonido y generar condiciones sonoras más localizadas.

**Enfoque metodológico**  
Este estudio evalúa cómo la distancia entre grabadoras afecta la independencia de las muestras acústicas. Al probar distancias de 15 m, 30 m y 45 m en bosque y pastizal, buscamos identificar a qué distancia los AudioMoth comienzan a capturar información sonora diferente bajo las condiciones locales del sitio de estudio.

---

## 14. Recommended next task for the new chat

The new chat should help with one of these:

1. Revise the slide deck again using the corrected non-paired design.
2. Decide whether to reuse the same points or move to new points after each 2-day spacing treatment.
3. Build a final field schedule for 6 AudioMoths and 6 field days.
4. Write the final methods section in English and Spanish.
5. Create a simple analysis plan that avoids overclaiming and avoids pseudoreplication.
