# =============================================================================
# Frog runner: scores every clip in DAY's window with the Ecuadorian custom
# BirdNET frog classifier (from the course "Clasificador de Ranas") and caches
# detections (with start/end) to outputs/<DAY>/frog_detections.csv.
# Same shape as run_birdnet_day1.R so it flows into the same gallery/analysis.
# =============================================================================
options(timeout = 1800)
source(file.path("d:/Audiomoths", "tandayapa_common.R"))
suppressMessages({ library(birdnetR); library(readr) })

DAY       <- Sys.getenv("TANDAYAPA_DAY", "day1")   # override: set TANDAYAPA_DAY
MIN_CONF  <- 0.25
FROG_DIR  <- "d:/Audiomoths/models/frog_classifier_ec"
OUT       <- day_dir(DAY)
det_csv   <- file.path(OUT, "frog_detections.csv")

wav_files <- build_inventory(DAY)
cat("Clips to score (", DAY, "):", nrow(wav_files), "\n")

cat("Loading custom frog model...\n")
model <- birdnet_model_custom(version = "v2.4",
                              classifier_folder = FROG_DIR,
                              classifier_name = "CustomClassifier")

## Labels carry a reference-library tag, e.g. "Pristimantis achantinus (QC)".
## Strip it to clean binomials.
clean_name <- function(x) trimws(sub("\\s*[(]?(QC|AG)[)]?\\s*$", "", x))

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
    d$scientific_name <- clean_name(d$scientific_name)
    d$common_name     <- clean_name(d$common_name)
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
cat("DONE.", nrow(bind_rows(acc)), "frog detections ->", det_csv, "\n")
cat("Total time:", round(as.numeric(difftime(Sys.time(), t0, units = "mins")), 1), "min\n")
