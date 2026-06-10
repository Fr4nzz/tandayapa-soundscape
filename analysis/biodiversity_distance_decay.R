# =============================================================================
# Tandayapa recorder-spacing study — biodiversity (species-community) analysis.
#
# Research question: does the SPECIES COMMUNITY recorded by two AudioMoths become
# more different as the distance between them grows, and is that distance-decay
# steeper in forest than in pasture?
#
#   Response  = pairwise community dissimilarity between two within-habitat
#               recorders in the same deployment:
#                 - Bray-Curtis on detection abundance (vegan::vegdist)
#                 - Jaccard on presence/absence
#   Predictor = nominal inter-recorder distance = spacing * |point_i - point_j|
#   Replication = each spacing (15/30/60 m) was deployed on TWO separate days,
#               so the deploy day is a replicate BLOCK -> random intercept (1|deploy).
#               Recorder pairs share recorders -> not independent; the random
#               effect + honest small-n caveats handle the pilot design.
#
# Reads the BirdNET web detections (outputs/web/day*.json) so it is independent of
# the Windows raw-audio tree. Drops the expert-flagged false-positive frog taxa
# (data/excluded_frog_taxa.csv) and keeps insects (validated reliable).
#
# Run:  Rscript analysis/biodiversity_distance_decay.R
# Needs: jsonlite, dplyr, tidyr, purrr, vegan, lme4, lmerTest, ggplot2
# =============================================================================

suppressMessages({
  library(jsonlite); library(dplyr); library(tidyr); library(purrr)
  library(vegan); library(lme4); library(lmerTest); library(ggplot2)
})

CONF_MIN <- 0.25                      # match the web app default (taxa validated there)
here     <- function(...) file.path(getwd(), ...)
out_dir  <- here("outputs", "analysis"); dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)

## --- authoritative deploy -> recorder map (from tandayapa_common.R DEVICES) -----
devices <- tribble(
  ~device,             ~deploy, ~habitat,  ~point,
  "F1501_A05","day1","forest",1, "F1502_A06","day1","forest",2, "F1503_A08","day1","forest",3,
  "P1501_A04","day1","pasture",1,"P1502_A01","day1","pasture",2,"P1503_A02","day1","pasture",3,
  "F3001_A01","day2","forest",1, "F3002_A05","day2","forest",2, "F3003_A07","day2","forest",3,
  "P3001_A06","day2","pasture",1,"P3002_A04","day2","pasture",2,
  "F6002_A03","day3","forest",2, "F6003_A05","day3","forest",3, "P6002_A02","day3","pasture",2,
  "F1501_A07","day4","forest",1, "F1502_A01","day4","forest",2,
  "P1501_A02","day4","pasture",1,"P1502_A05","day4","pasture",2,"P1503_A03","day4","pasture",3,
  "F3001_A02","day5","forest",1, "F3002_A03","day5","forest",2, "F3003_A01","day5","forest",3,
  "P3001_A05","day5","pasture",1,"P3002_A04_6julio","day5","pasture",2,"P3003_A06","day5","pasture",3,
  "F6002_A05","day6","forest",2, "F6003_A06","day6","forest",3,
  "P6001_A02","day6","pasture",1,"P6003_A01","day6","pasture",3
)
day_spacing <- c(day1=15, day2=30, day3=60, day4=15, day5=30, day6=60)

## --- load detections ----------------------------------------------------------
excluded <- if (file.exists(here("data","excluded_frog_taxa.csv")))
  read.csv(here("data","excluded_frog_taxa.csv"))$species else character(0)

day_files <- list.files(here("outputs","web"), pattern = "^day[0-9]+\\.json$", full.names = TRUE)
dets <- map_dfr(day_files, ~ as_tibble(fromJSON(.x))) %>%
  transmute(group, species, conf, device = sub("^/([^/]+)/.*$", "\\1", audio)) %>%
  inner_join(devices, by = "device") %>%   # devices supplies habitat/point/deploy (avoid JSON habitat clash)
  filter(!species %in% excluded, conf >= CONF_MIN) %>%
  mutate(spacing = day_spacing[deploy])

message(sprintf("detections kept: %d  (conf >= %.2f, %d excluded-frog taxa removed)",
                nrow(dets), CONF_MIN, length(excluded)))

## --- descriptive richness -----------------------------------------------------
richness <- dets %>% group_by(habitat, group) %>% summarise(n = n_distinct(species), .groups="drop") %>%
  pivot_wider(names_from = group, values_from = n, values_fill = 0)
richness$TOTAL <- dets %>% group_by(habitat) %>% summarise(n = n_distinct(species)) %>% pull(n)
write.csv(richness, file.path(out_dir, "richness_by_habitat_R.csv"), row.names = FALSE)
print(richness)

## --- community matrix: rows = (deploy,habitat,point), cols = species ----------
comm_long <- dets %>% count(deploy, habitat, point, species, name = "abund")
samples   <- comm_long %>% distinct(deploy, habitat, point) %>% mutate(sample = row_number())
mat <- comm_long %>% left_join(samples, by=c("deploy","habitat","point")) %>%
  pivot_wider(id_cols = sample, names_from = species, values_from = abund, values_fill = 0)
M  <- as.matrix(mat[,-1]); rownames(M) <- mat$sample

bc <- as.matrix(vegdist(M, method = "bray"))
ja <- as.matrix(vegdist(M > 0, method = "jaccard"))

## --- within-habitat recorder pairs -------------------------------------------
pairs <- list()
for (g in split(samples, list(samples$deploy, samples$habitat), drop = TRUE)) {
  if (nrow(g) < 2) next
  cb <- combn(seq_len(nrow(g)), 2)
  for (k in seq_len(ncol(cb))) {
    i <- g[cb[1,k],]; j <- g[cb[2,k],]
    pairs[[length(pairs)+1]] <- tibble(
      deploy = i$deploy, habitat = i$habitat,
      distance_m = day_spacing[i$deploy] * abs(i$point - j$point),
      bray = bc[as.character(i$sample), as.character(j$sample)],
      jacc = ja[as.character(i$sample), as.character(j$sample)])
  }
}
pw <- bind_rows(pairs) %>% mutate(distance_z = as.numeric(scale(distance_m)))
write.csv(pw, file.path(out_dir, "pairwise_dissimilarity_R.csv"), row.names = FALSE)
message(sprintf("within-habitat pairs: %d (forest %d, pasture %d); distances: %s m",
        nrow(pw), sum(pw$habitat=="forest"), sum(pw$habitat=="pasture"),
        paste(sort(unique(pw$distance_m)), collapse=", ")))

## --- mixed models: dissim ~ distance * habitat + (1 | deploy) -----------------
sink(file.path(out_dir, "model_summary_R.txt"))
for (resp in c("bray","jacc")) {
  cat("\n================= ", resp, " =================\n")
  f <- as.formula(sprintf("%s ~ distance_z * habitat + (1 | deploy)", resp))
  m <- tryCatch(lmer(f, data = pw), error = function(e) e)
  if (inherits(m, "error")) { cat("lmer failed:", conditionMessage(m), "\n");
    print(summary(lm(as.formula(sprintf("%s ~ distance_z * habitat", resp)), data = pw))) ;
    next }
  print(summary(m)$coefficients)
  ## per-habitat distance slope (simple lm, for the figure / interpretation)
  for (h in c("forest","pasture")) {
    d <- filter(pw, habitat == h)
    cf <- coef(summary(lm(get(resp) ~ distance_m, data = d)))
    cat(sprintf("  %-8s slope = %+.5f /m  (per +10 m %+.4f)  p = %.4f  n=%d\n",
                h, cf[2,1], cf[2,1]*10, cf[2,4], nrow(d)))
  }
}
sink()
cat(readLines(file.path(out_dir, "model_summary_R.txt")), sep = "\n")

## --- figures ------------------------------------------------------------------
cols <- c(forest = "#2C5F2D", pasture = "#D9A441")
p1 <- ggplot(pw, aes(distance_m, bray, color = habitat)) +
  geom_point(size = 2.6, alpha = .8) + geom_smooth(method = "lm", se = TRUE, linewidth = 1) +
  scale_color_manual(values = cols) +
  labs(x = "Distance between recorders (m)", y = "Community dissimilarity (Bray-Curtis)",
       title = "Acoustic community distance-decay · forest vs pasture") + theme_minimal()
ggsave(file.path(out_dir, "fig1_distance_decay_braycurtis_R.png"), p1, width = 6.4, height = 4.4, dpi = 150)

p2 <- ggplot(pw, aes(distance_m, jacc, color = habitat)) +
  geom_point(size = 2.6, alpha = .8) + geom_smooth(method = "lm", se = TRUE, linewidth = 1) +
  scale_color_manual(values = cols) +
  labs(x = "Distance between recorders (m)", y = "Community dissimilarity (Jaccard)",
       title = "Species turnover with distance · forest vs pasture") + theme_minimal()
ggsave(file.path(out_dir, "fig2_distance_decay_jaccard_R.png"), p2, width = 6.4, height = 4.4, dpi = 150)

message("Done. Outputs in outputs/analysis/ (…_R.* files).")
