# =============================================================================
# Shared config + helpers for the Tandayapa pipeline.
# Sourced by the standalone runners (run_birdnet*.R, birdnet_location_filter.R,
# build_gallery_report.R, build_gallery_site.R) AND the per-day Rmd. Keeps devices,
# time zone, windows, spacing and the file inventory identical across scripts.
# Each runner sets DAY <- "dayN" and calls day_dir(DAY) / build_inventory(DAY).
# Add a new day by appending rows to DEVICES (with its `day`) and entries to
# DAY_WINDOWS / DAY_WEEK / DAY_SPACING.
# =============================================================================
suppressMessages({
  library(dplyr); library(stringr); library(tidyr)
  library(purrr); library(lubridate); library(tibble)
})

ROOT_DIR <- "d:/Audiomoths"
OUT_ROOT <- file.path(ROOT_DIR, "outputs")
TZ       <- "America/Guayaquil"   # Ecuador, UTC-5, no DST

## Device metadata, per deployment day. offset_h = hours to ADD to the filename
## time to get true local time (devices set to UTC are 5 h fast -> -5).
## NOTE day2 point reuse: day2 point1 == day1 point1 spot; day2 point2 == day1
## point3 spot; day2 point3 is new (30 m further). P3003_A03 excluded (failed).
DEVICES <- tribble(
  ~deploy, ~folder,     ~habitat,  ~point, ~moth_id, ~offset_h,
  # ---- day1: 15 m spacing (2026-06-02) ----
  "day1",  "F1501_A05", "forest",   1L,    "A05",     0,
  "day1",  "F1502_A06", "forest",   2L,    "A06",     0,
  "day1",  "F1503_A08", "forest",   3L,    "A08",    -5,
  "day1",  "P1501_A04", "pasture",  1L,    "A04",     0,
  "day1",  "P1502_A01", "pasture",  2L,    "A01",     0,
  "day1",  "P1503_A02", "pasture",  3L,    "A02",     0,
  # ---- day2: 30 m spacing (2026-06-03) ----
  "day2",  "F3001_A01", "forest",   1L,    "A01",     0,
  "day2",  "F3002_A05", "forest",   2L,    "A05",     0,
  "day2",  "F3003_A07", "forest",   3L,    "A07",    -5,
  "day2",  "P3001_A06", "pasture",  1L,    "A06",     0,
  "day2",  "P3002_A04", "pasture",  2L,    "A04",     0
)

## Per-day analysis window (LOCAL time, after clock correction).
DAY_WINDOWS <- list(
  day1 = c("2026-06-02 10:40:00", "2026-06-03 09:40:00"),
  day2 = c("2026-06-03 11:40:00", "2026-06-04 09:40:00")
)

## Recorder spacing (m) per day -> distance between points i,j on the line.
DAY_SPACING <- list(day1 = 15, day2 = 30)

## BirdNET range-filter week per day (1-48, ~4 per month). Early June ~ 21.
DAY_WEEK <- list(day1 = 21, day2 = 21)

## Distance (m) between two points given the day's spacing (equal-spaced line).
point_distance_m <- function(day, i, j) DAY_SPACING[[day]] * abs(i - j)

## outputs/<day>/ (created on demand, with a clips/ subfolder)
day_dir <- function(day) {
  d <- file.path(OUT_ROOT, day)
  dir.create(file.path(d, "clips"), recursive = TRUE, showWarnings = FALSE)
  d
}

parse_moth_time <- function(fname, tz = TZ) {
  ts <- str_match(basename(fname), "(\\d{8})_(\\d{6})")
  ymd_hms(paste(ts[, 2], ts[, 3]), tz = tz)
}

## File inventory for a day: one row per clip in the window, clock-corrected.
build_inventory <- function(day) {
  w <- DAY_WINDOWS[[day]]
  if (is.null(w)) stop("No window defined for ", day, " in DAY_WINDOWS")
  ws <- ymd_hms(w[1], tz = TZ); we <- ymd_hms(w[2], tz = TZ)
  this_deploy <- day
  DEVICES %>%
    filter(deploy == this_deploy) %>%
    mutate(paths = map(folder, ~ list.files(file.path(ROOT_DIR, .x),
                       pattern = "\\.WAV$", full.names = TRUE, ignore.case = TRUE))) %>%
    unnest(paths) %>%
    mutate(time = parse_moth_time(paths) + hours(offset_h),
           hour = floor_date(time, "hour"), day = as_date(time),
           file = basename(paths),
           recorder = paste0(toupper(substr(habitat, 1, 1)), point)) %>%
    filter(!is.na(time), time >= ws, time <= we) %>%
    arrange(habitat, point, time)
}
