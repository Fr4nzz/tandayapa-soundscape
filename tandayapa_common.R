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
  "day2",  "P3002_A04", "pasture",  2L,    "A04",     0,
  # ---- day3: 60 m spacing (2026-06-04). forest p1 (F6001) missing;
  #            pasture p1 (P6001) & p3 (P6003) SD cards failed -> pasture p2 only ----
  "day3",  "F6002_A03", "forest",   2L,    "A03",     0,
  "day3",  "F6003_A05", "forest",   3L,    "A05",     0,
  "day3",  "P6002_A02", "pasture",  2L,    "A02",     0,
  # ---- day4: 15 m spacing (2026-06-05). forest p3 (F1503_A06) failed (USB mode).
  #            forest p2 had TWO co-located recorders (A01 + A04) as backup; we use
  #            A01 as p2 (A04 left out = a 0 m same-spot agreement control). ----
  "day4",  "F1501_A07", "forest",   1L,    "A07",     0,
  "day4",  "F1502_A01", "forest",   2L,    "A01",     0,
  "day4",  "P1501_A02", "pasture",  1L,    "A02",     0,
  "day4",  "P1502_A05", "pasture",  2L,    "A05",     0,
  "day4",  "P1503_A03", "pasture",  3L,    "A03",     0,
  # ---- day5: 30 m spacing (2026-06-06). full 3+3 (cleanest new round).
  #            (P6003_A07_7Jun is a 60 m pasture-p3 recovery run, NOT day5 -> excluded) ----
  "day5",  "F3001_A02", "forest",   1L,    "A02",     0,
  "day5",  "F3002_A03", "forest",   2L,    "A03",     0,
  "day5",  "F3003_A01", "forest",   3L,    "A01",     0,
  "day5",  "P3001_A05", "pasture",  1L,    "A05",     0,
  "day5",  "P3002_A04_6julio", "pasture", 2L, "A04",  0,
  "day5",  "P3003_A06", "pasture",  3L,    "A06",     0,
  # ---- day6: 60 m spacing (2026-06-07, last day). 2 dead SD cards:
  #            forest p1 (F6001) & pasture p2 (P6002) -> forest p2-p3, pasture p1-p3 ----
  "day6",  "F6002_A05", "forest",   2L,    "A05",     0,
  "day6",  "F6003_A06", "forest",   3L,    "A06",     0,
  "day6",  "P6001_A02", "pasture",  1L,    "A02",     0,
  "day6",  "P6003_A01", "pasture",  3L,    "A01",     0
)

## Per-day analysis window (LOCAL time, after clock correction).
## Standard window for new rounds is 11:00:00 -> 09:42:00 (09:42-11:00 = repositioning).
DAY_WINDOWS <- list(
  day1 = c("2026-06-02 10:40:00", "2026-06-03 09:40:00"),
  day2 = c("2026-06-03 11:40:00", "2026-06-04 09:40:00"),
  day3 = c("2026-06-04 11:00:00", "2026-06-05 09:42:00"),
  day4 = c("2026-06-05 11:00:00", "2026-06-06 09:42:00"),
  day5 = c("2026-06-06 11:00:00", "2026-06-07 09:42:00"),
  day6 = c("2026-06-07 11:00:00", "2026-06-08 09:42:00")
)

## Recorder spacing (m) per day -> distance between points i,j on the line.
DAY_SPACING <- list(day1 = 15, day2 = 30, day3 = 60, day4 = 15, day5 = 30, day6 = 60)

## BirdNET range-filter week per day (1-48, ~4 per month). Early June ~ 21.
DAY_WEEK <- list(day1 = 21, day2 = 21, day3 = 21, day4 = 21, day5 = 21, day6 = 21)

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
