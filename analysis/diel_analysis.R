#!/usr/bin/env Rscript
# Diel variation of acoustic indices (ACI, BI, ADI) by time of day x habitat.
# Answers the friends' Prediction 3 ("what happens during dawn and dusk?").
# Effect sizes = each diel period vs NIGHT (mixed model, recorder random intercept).
suppressMessages({library(dplyr); library(tidyr); library(lme4); library(ggplot2)})

OUT <- "outputs/analysis"
cols <- c(forest = "#2C5F2D", pasture = "#D9A441")
d <- read.csv(file.path(OUT, "diel_indices.csv"))
d$diel <- factor(d$diel, levels = c("night", "dawn", "day", "dusk"))

# ---- effect sizes: diel period vs night, per habitat, per index ----
es <- list()
for (idx in c("ACI", "BI", "ADI")) {
  m <- suppressWarnings(lmer(reformulate("diel*habitat + (1|device)", idx), data = d, REML = TRUE))
  b <- fixef(m); V <- as.matrix(vcov(m))
  for (h in c("forest", "pasture")) for (p in c("dawn", "day", "dusk")) {
    terms <- if (h == "forest") paste0("diel", p) else c(paste0("diel", p), paste0("diel", p, ":habitatpasture"))
    est <- sum(b[terms]); se <- sqrt(sum(V[terms, terms]))
    es[[length(es) + 1]] <- data.frame(index = idx, habitat = h, period = p,
      vs_night = round(est, 3), ci_lo = round(est - 1.96 * se, 3), ci_hi = round(est + 1.96 * se, 3),
      excl0 = ifelse((est - 1.96 * se) > 0 | (est + 1.96 * se) < 0, "yes", "no"))
  }
}
es <- bind_rows(es)
write.csv(es, file.path(OUT, "diel_effect_sizes.csv"), row.names = FALSE)
print(es)

# ---- figure: mean +/- 95% CI by diel x habitat, faceted by index ----
summ <- d %>%
  pivot_longer(c(ACI, BI, ADI), names_to = "index", values_to = "value") %>%
  mutate(index = factor(index, levels = c("ACI", "BI", "ADI"))) %>%
  group_by(index, habitat, diel) %>%
  summarise(mean = mean(value), se = sd(value) / sqrt(n()), .groups = "drop") %>%
  mutate(lo = mean - 1.96 * se, hi = mean + 1.96 * se)

p <- ggplot(summ, aes(diel, mean, color = habitat, group = habitat)) +
  geom_line(linewidth = .9) +
  geom_point(size = 2.6) +
  geom_errorbar(aes(ymin = lo, ymax = hi), width = .15) +
  scale_color_manual(values = cols) +
  facet_wrap(~index, scales = "free_y") +
  labs(x = "Time of day", y = "Index value (mean ± 95% CI)",
       title = "Diel variation of acoustic indices · forest vs pasture") +
  theme_minimal() + theme(axis.text.x = element_text(angle = 0))
ggsave(file.path(OUT, "fig5_diel_indices.png"), p, width = 9, height = 3.6, dpi = 150)
cat("wrote diel_effect_sizes.csv + fig5_diel_indices.png\n")
