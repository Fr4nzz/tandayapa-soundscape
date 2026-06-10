#!/usr/bin/env Rscript
# Cleaner, model-faithful index distance-decay graphs for the oral presentation.
# Each panel shows the MIXED-MODEL fixed-effect fit (|Δindex| ~ distance + (1|deploy))
# with its 95% band, and points adjusted for the deploy (day) random intercept
# (partial residuals = observed - deploy BLUP), so day-to-day baseline scatter is
# removed and the points hug the model line -> reflects the model + looks cleaner.
suppressMessages({library(dplyr); library(tidyr); library(lme4); library(ggplot2); library(purrr)})

OUT <- "outputs/analysis"
cols <- c(forest = "#2C5F2D", pasture = "#D9A441")
idx <- read.csv(file.path(OUT, "acoustic_indices.csv"))

# pairwise |Δindex| within habitat & deploy
ip <- list()
for (g in split(idx, list(idx$deploy, idx$habitat), drop = TRUE)) {
  if (nrow(g) < 2) next
  cb <- combn(seq_len(nrow(g)), 2)
  for (k in seq_len(ncol(cb))) {
    a <- g[cb[1, k], ]; b <- g[cb[2, k], ]
    ip[[length(ip) + 1]] <- tibble(deploy = a$deploy, habitat = a$habitat,
      distance_m = a$spacing * abs(a$point - b$point),
      dACI = abs(a$ACI - b$ACI), dBI = abs(a$BI - b$BI), dADI = abs(a$ADI - b$ADI))
  }
}
ipw <- bind_rows(ip) %>% filter(distance_m <= 60)   # exclude the lone 120 m pasture pair

rep_of <- function(d) ifelse(d %in% c("day1","day2","day3"), "1st day", "2nd day")
relab <- c(dACI = "ACI", dBI = "BI", dADI = "ADI")
pts <- list(); lns <- list()
for (r in c("dACI", "dBI", "dADI")) {
  for (h in c("forest", "pasture")) {
    s <- filter(ipw, habitat == h)
    m <- suppressWarnings(lmer(reformulate("distance_m + (1|deploy)", r), data = s, REML = TRUE))
    # deploy-adjusted (partial-residual) points: observed - deploy BLUP
    bl <- ranef(m)$deploy[, 1]; names(bl) <- rownames(ranef(m)$deploy)
    adj <- s[[r]] - bl[as.character(s$deploy)]
    pts[[length(pts) + 1]] <- tibble(index = relab[[r]], habitat = h,
                                     distance_m = s$distance_m, y = adj, rep = rep_of(s$deploy))
    # fixed-effect line + 95% band
    g <- tibble(distance_m = seq(min(s$distance_m), max(s$distance_m), length = 50))
    X <- cbind(1, g$distance_m); V <- as.matrix(vcov(m))
    g$fit <- as.numeric(X %*% fixef(m)); g$se <- sqrt(diag(X %*% V %*% t(X)))
    lns[[length(lns) + 1]] <- tibble(index = relab[[r]], habitat = h,
      distance_m = g$distance_m, fit = g$fit, lo = g$fit - 1.96 * g$se, hi = g$fit + 1.96 * g$se)
  }
}
pts <- bind_rows(pts) %>% mutate(index = factor(index, levels = c("ACI","BI","ADI")))
lns <- bind_rows(lns) %>% mutate(index = factor(index, levels = c("ACI","BI","ADI")))

p <- ggplot() +
  geom_ribbon(data = lns, aes(distance_m, ymin = lo, ymax = hi, fill = habitat), alpha = .15) +
  geom_line(data = lns, aes(distance_m, fit, color = habitat), linewidth = 1) +
  geom_point(data = pts, aes(distance_m, y, color = habitat, shape = rep), size = 2.2, alpha = .8) +
  scale_color_manual(values = cols) + scale_fill_manual(values = cols) +
  scale_shape_manual(values = c("1st day" = 16, "2nd day" = 17), name = "replicate") +
  facet_wrap(~index, scales = "free_y") +
  labs(x = "Distance between recorders (m)",
       y = "|index difference| (day-adjusted)",
       title = "Acoustic-index distance-decay (≤60 m) · mixed-model fit (day as random factor)",
       subtitle = "Line = model fit, band = 95% CI; points day-adjusted, shape = replicate day. All indices flat.") +
  theme_minimal()
ggsave(file.path(OUT, "fig_index_distance_clean.png"), p, width = 9, height = 3.8, dpi = 150)
cat("wrote fig_index_distance_clean.png\n")
