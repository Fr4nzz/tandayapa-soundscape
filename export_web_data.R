# =============================================================================
# Export per-day detection JSON for the React web app (webapp/).
# Scans every outputs/<day>/ with detections, merges bird (range-filtered) + frog,
# attaches the served audio URL, and writes:
#   outputs/web/<day>.json   - array of detections
#   outputs/web/index.json   - summary (days, taxa, recorders, species, ...)
# Audio is served from the repo root over the LAN, so audio = "/<folder>/<file>".
# Re-run whenever any pipeline updates detections.  Rscript export_web_data.R
# =============================================================================
source(file.path("d:/Audiomoths", "tandayapa_common.R"))
suppressMessages({ library(readr); library(jsonlite); library(purrr) })

web_dir <- file.path(OUT_ROOT, "web")
dir.create(web_dir, showWarnings = FALSE, recursive = TRUE)

## Load one detections CSV, tag taxon group; optional range filter (birds).
load_det <- function(csv, group, range_csv = NULL) {
  if (!file.exists(csv)) return(NULL)
  d <- suppressWarnings(read_csv(csv, show_col_types = FALSE)) %>%
    mutate(time = with_tz(time, TZ)) %>%
    filter(!is.na(scientific_name), !is.na(confidence))
  if (!all(c("start", "end") %in% names(d))) return(NULL)   # need detection times
  if (!"common_name" %in% names(d)) d$common_name <- d$scientific_name
  if (!is.null(range_csv) && file.exists(range_csv)) {
    allowed <- read_csv(range_csv, show_col_types = FALSE) %>% mutate(sci = sub("_.*$", "", label))
    d <- d %>% filter(scientific_name %in% allowed$sci)
  }
  mutate(d, group = group)
}

## BirdNET v2.4 also classifies Orthoptera/Cicadidae. The species are temperate
## (wrong here), but we keep them at GENUS level, flagged "~", as a coarse insect
## signal — family is the only fully safe level, so treat genus as approximate.
INSECT_PAT <- paste0("katydid|conehead|cricket|cicada|grasshopper|shieldback|Orthoptera|",
  "Neoconocephalus|Conocephalus|Amblycorypha|Gryllus|Tettigon|Oecanthus|Anaxipha|",
  "Allonemobius|Microcentrum|Scudderia|Pterophylla|Atlanticus|Magicicada|Neotibicen|Tibicen|Okanagana|Acheta")
insect_type <- function(sci, common) {
  g <- sub(" .*$", "", sci)
  cricket <- grepl("cricket", common, ignore.case = TRUE) |
    g %in% c("Gryllus","Acheta","Oecanthus","Anaxipha","Allonemobius","Gryllodes","Miogryllus")
  cicada  <- grepl("cicada", common, ignore.case = TRUE) |
    g %in% c("Magicicada","Neotibicen","Tibicen","Okanagana")
  ifelse(cicada, "cicada", ifelse(cricket, "cricket", "katydid"))
}
load_insects <- function(csv) {
  if (!file.exists(csv)) return(NULL)
  d <- suppressWarnings(read_csv(csv, show_col_types = FALSE)) %>%
    mutate(time = with_tz(time, TZ)) %>%
    filter(!is.na(scientific_name), !is.na(confidence))
  if (!all(c("start", "end") %in% names(d))) return(NULL)
  if (!"common_name" %in% names(d)) d$common_name <- d$scientific_name
  d <- d %>% filter(grepl(INSECT_PAT, common_name, ignore.case = TRUE) |
                    grepl(INSECT_PAT, scientific_name, ignore.case = TRUE))
  if (nrow(d) == 0) return(NULL)
  genus <- sub(" .*$", "", d$scientific_name)
  type  <- insect_type(d$scientific_name, d$common_name)
  d %>% mutate(group = "insect",
               common_name     = paste0("~ ", genus, " (", type, ")"),  # genus-level, approximate
               scientific_name = genus)
}

export_day <- function(day) {
  OUT <- day_dir(day)
  sp  <- DAY_SPACING[[day]]
  det <- bind_rows(
    load_det(file.path(OUT, "birdnet_detections.csv"), "bird",
             file.path(OUT, "birdnet_location_species.csv")),
    load_det(file.path(OUT, "frog_detections.csv"), "frog"),
    load_insects(file.path(OUT, "birdnet_detections.csv"))   # BirdNET insect classes -> genus
  )
  if (is.null(det) || nrow(det) == 0) return(NULL)
  inv <- build_inventory(day)

  det <- det %>%
    left_join(inv %>% select(folder, time, file), by = c("folder", "time")) %>%
    filter(!is.na(file)) %>%
    mutate(day      = day,
           spacing  = sp,
           audio    = paste0("/", folder, "/", file),
           recorder = paste0(toupper(substr(habitat, 1, 1)), point),
           daynight = ifelse(hour(time) >= 6 & hour(time) < 18, "day", "night"),
           id       = sprintf("%s-%05d", day, row_number())) %>%
    arrange(desc(confidence))

  records <- det %>%
    transmute(id, day, group, audio, start = round(start, 2), end = round(end, 2),
              species = scientific_name, common = common_name, conf = round(confidence, 3),
              habitat, recorder, moth = moth_id,
              time = format(time, "%Y-%m-%d %H:%M:%S"),
              hour = hour(time), daynight, spacing)

  write_json(records, file.path(web_dir, paste0(day, ".json")), auto_unbox = TRUE, digits = 4)

  list(day = day, spacing = sp,
       window = I(unname(DAY_WINDOWS[[day]])), n = nrow(records),
       groups = as.list(table(records$group)),
       recorders = I(sort(unique(records$recorder))),
       habitats  = I(sort(unique(records$habitat))),
       species   = I(sort(unique(records$common))))
}

days <- names(DAY_WINDOWS)
summaries <- compact(map(days, export_day))

index <- list(
  generated = format(Sys.time(), "%Y-%m-%d %H:%M"),
  days      = summaries,
  groups    = I(sort(unique(unlist(map(summaries, ~ names(.x$groups)))))),
  recorders = I(sort(unique(unlist(map(summaries, "recorders"))))),
  habitats  = I(sort(unique(unlist(map(summaries, "habitats"))))),
  species   = I(sort(unique(unlist(map(summaries, "species")))))
)
write_json(index, file.path(web_dir, "index.json"), auto_unbox = TRUE, pretty = TRUE)

cat("Exported", length(summaries), "day(s) ->", web_dir, "\n")
for (s in summaries) cat(sprintf("  %s: %d detections (%s)\n", s$day, s$n,
  paste(names(s$groups), unlist(s$groups), sep = "=", collapse = ", ")))
