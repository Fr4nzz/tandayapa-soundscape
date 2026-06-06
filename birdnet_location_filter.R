# Compute BirdNET's expected species list for Tandayapa at the deployment time
# (range filter), per DAY. Writes outputs/<DAY>/birdnet_location_species.csv.
# The Rmd / gallery post-filter detections to this list to cut out-of-range FPs.
source(file.path("d:/Audiomoths", "tandayapa_common.R"))
suppressMessages({ library(birdnetR); library(readr) })

DAY <- Sys.getenv("TANDAYAPA_DAY", "day1")   # override: set TANDAYAPA_DAY
OUT <- day_dir(DAY)
LAT <- -0.006; LON <- -78.681      # Tandayapa Bird Lodge area, Ecuador
WEEK <- DAY_WEEK[[DAY]]            # 1-48, ~4 per month; early June ~ 21
LOC_MIN_CONF <- 0.03

## Range filter uses BirdNET's META model (location/time -> species),
## separate from the audio (tflite) model.
meta <- birdnet_model_meta("v2.4")
loc <- predict_species_at_location_and_time(meta, latitude = LAT, longitude = LON,
                                            week = WEEK, min_confidence = LOC_MIN_CONF)
cat("species expected at Tandayapa,", DAY, "(week", WEEK, "):", nrow(loc), "\n")
out_csv <- file.path(OUT, "birdnet_location_species.csv")
write_csv(as.data.frame(loc), out_csv)
cat("written ->", out_csv, "\n")
