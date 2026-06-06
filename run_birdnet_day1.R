# =============================================================================
# BirdNET runner (heavy Python/TensorFlow). Scores every clip in DAY's window
# and caches detections (with start/end) to outputs/<DAY>/birdnet_detections.csv.
# Set DAY below; run once per day.  (Distinct from the other pipeline's run_birdnet.R.)
# =============================================================================
options(timeout = 1800)
source(file.path("d:/Audiomoths", "tandayapa_common.R"))
suppressMessages({ library(birdnetR); library(readr) })

DAY      <- Sys.getenv("TANDAYAPA_DAY", "day1")   # override: set TANDAYAPA_DAY
MIN_CONF <- 0.25
OUT      <- day_dir(DAY)
det_csv  <- file.path(OUT, "birdnet_detections.csv")

wav_files <- build_inventory(DAY)
cat("Clips to score (", DAY, "):", nrow(wav_files), "\n")

cat("Loading BirdNET model...\n")
model <- birdnet_model_tflite("v2.4")

score_one <- function(path) {
  res <- try(suppressWarnings(suppressMessages(
    predict_species_from_audio_file(model, path, min_confidence = MIN_CONF, keep_empty = FALSE)
  )), silent = TRUE)
  if (inherits(res, "try-error") || is.null(res) || nrow(res) == 0)
    return(tibble(start = numeric(), end = numeric(), scientific_name = character(),
                  common_name = character(), confidence = numeric()))
  as_tibble(res)[, c("start", "end", "scientific_name", "common_name", "confidence")]
}

t0 <- Sys.time(); n <- nrow(wav_files); acc <- vector("list", n)
for (i in seq_len(n)) {
  d <- score_one(wav_files$paths[i])
  if (nrow(d) > 0) {
    d$folder <- wav_files$folder[i]; d$habitat <- wav_files$habitat[i]
    d$point  <- wav_files$point[i];  d$moth_id <- wav_files$moth_id[i]
    d$time   <- wav_files$time[i];   d$hour    <- wav_files$hour[i]
    d$day    <- wav_files$day[i]
  }
  acc[[i]] <- d
  if (i %% 25 == 0 || i == n)
    cat(sprintf("  %d/%d clips (%.1f min)\n", i, n,
                as.numeric(difftime(Sys.time(), t0, units = "mins"))))
}

write_csv(bind_rows(acc), det_csv)
cat("DONE.", nrow(bind_rows(acc)), "detections ->", det_csv, "\n")
cat("Total time:", round(as.numeric(difftime(Sys.time(), t0, units = "mins")), 1), "min\n")
