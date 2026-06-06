# =============================================================================
# Build the BirdNET validation gallery embedded in the Rmd report, per DAY:
# for the top-confidence detections, export a spectrogram PNG (labeled time-boxes)
# + a short playable WAV to outputs/<DAY>/clips/, and a manifest the Rmd renders.
# Run AFTER run_birdnet_day1.R.  (Distinct from the other pipeline's build_gallery.R.)
# =============================================================================
source(file.path("d:/Audiomoths", "tandayapa_common.R"))
suppressMessages({ library(birdnetR); library(tuneR); library(seewave); library(readr) })

DAY       <- Sys.getenv("TANDAYAPA_DAY", "day1")   # override: set TANDAYAPA_DAY
OUT       <- day_dir(DAY)
clips_dir <- file.path(OUT, "clips")
det_csv   <- file.path(OUT, "birdnet_detections.csv")
manifest  <- file.path(OUT, "gallery_manifest.csv")
MIN_CONF  <- 0.25
N_GALLERY <- 12
WIN_PAD   <- 4.5
FLIM_KHZ  <- c(0, 12)

inv <- build_inventory(DAY)       # folder, time, paths, habitat, point, moth_id

det <- read_csv(det_csv, show_col_types = FALSE) %>% mutate(time = with_tz(time, TZ)) %>%
  filter(!is.na(scientific_name), !is.na(confidence))
top_clips <- det %>%
  group_by(folder, time) %>% summarise(best_conf = max(confidence), .groups = "drop") %>%
  arrange(desc(best_conf)) %>% slice_head(n = N_GALLERY) %>%
  left_join(inv %>% select(folder, habitat, point, moth_id, time, paths),
            by = c("folder", "time"))
cat("Selected", nrow(top_clips), "clips for the", DAY, "gallery.\n")

model <- birdnet_model_tflite("v2.4")
rows <- list()
for (i in seq_len(nrow(top_clips))) {
  cl <- top_clips[i, ]
  w  <- readWave(cl$paths); dur <- length(w@left) / w@samp.rate
  d <- as_tibble(predict_species_from_audio_file(model, cl$paths, min_confidence = MIN_CONF)) %>%
    filter(!is.na(scientific_name), !is.na(confidence))
  top <- d %>% slice_max(confidence, n = 1, with_ties = FALSE)
  ws  <- max(0, top$start - WIN_PAD); we <- min(dur, top$end + WIN_PAD)
  win <- readWave(cl$paths, from = ws, to = we, units = "seconds")

  dd <- d %>% filter(end > ws, start < we) %>%
    group_by(start, end) %>% slice_max(confidence, n = 1, with_ties = FALSE) %>% ungroup() %>%
    mutate(rs = pmax(0, start - ws), re = pmin(we - ws, end - ws)) %>% arrange(rs)
  pal    <- c("#D7263D", "#1B9E77", "#7570B3", "#E6AB02", "#1f78b4", "#444444")
  sp_lev <- unique(dd$common_name)
  dd$col <- pal[(match(dd$common_name, sp_lev) - 1) %% length(pal) + 1]

  id <- sprintf("g%02d", i)
  png <- file.path(clips_dir, paste0(id, ".png")); wavf <- file.path(clips_dir, paste0(id, ".wav"))
  writeWave(win, wavf)
  grDevices::png(png, width = 950, height = 430, res = 96)
  spectro(win, flim = FLIM_KHZ, osc = FALSE, scale = FALSE, grid = FALSE,
          palette = reverse.gray.colors.1, cont = FALSE,
          main = sprintf("%s%d (%s)  %s", toupper(substr(cl$habitat, 1, 1)), cl$point,
                         cl$moth_id, format(cl$time, "%Y-%m-%d %H:%M")))
  for (k in seq_len(nrow(dd)))
    rect(dd$rs[k], FLIM_KHZ[1], dd$re[k], FLIM_KHZ[2], border = dd$col[k], lwd = 2)
  for (s in seq_along(sp_lev)) {
    sub  <- dd[dd$common_name == sp_lev[s], ]
    text(stats::median((sub$rs + sub$re) / 2), FLIM_KHZ[2] - 0.6 - (s - 1) * 1.05,
         sprintf("%s (%.2f)", sp_lev[s], max(sub$confidence)),
         col = sub$col[1], cex = 0.8, font = 2)
  }
  grDevices::dev.off()

  rows[[i]] <- tibble(
    id = id, habitat = cl$habitat, recorder = paste0(toupper(substr(cl$habitat, 1, 1)), cl$point),
    moth_id = cl$moth_id, time = cl$time, species = top$scientific_name,
    common = top$common_name, confidence = top$confidence, n_in_window = nrow(dd),
    png = file.path("outputs", DAY, "clips", paste0(id, ".png")),
    wav = file.path("outputs", DAY, "clips", paste0(id, ".wav")))
  cat(sprintf("  %2d/%d  %s  %s (%.2f)\n", i, nrow(top_clips), rows[[i]]$recorder,
              top$common_name, top$confidence))
}
write_csv(bind_rows(rows), manifest)
cat("DONE ->", manifest, "\n")
