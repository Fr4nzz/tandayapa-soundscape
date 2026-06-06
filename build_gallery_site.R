# =============================================================================
# Build the local sound-verification website for one DAY.
# Copies the shared site template into outputs/<DAY>/gallery_site/ and writes
# manifest.js (one record per range-filtered detection, pointing at the ORIGINAL
# clip served over the LAN). Run AFTER run_birdnet_day1.R (keeps start/end).
# =============================================================================
source(file.path("d:/Audiomoths", "tandayapa_common.R"))
suppressMessages({ library(readr); library(jsonlite) })

DAY      <- Sys.getenv("TANDAYAPA_DAY", "day1")   # override: set TANDAYAPA_DAY
OUT      <- day_dir(DAY)
template <- file.path(OUT_ROOT, "gallery_site_template")
site_dir <- file.path(OUT, "gallery_site")

## copy the shared shell (index/app/style/vendor/readme) into the per-day site
dir.create(site_dir, showWarnings = FALSE, recursive = TRUE)
file.copy(list.files(template, full.names = TRUE), site_dir, recursive = TRUE, overwrite = TRUE)

inv <- build_inventory(DAY)              # folder, time, file, recorder, habitat, point, moth_id

## Load one detections file, tag its taxon group. Birds get the location range
## filter; the frog model is already Ecuador-specific so it isn't range-filtered.
load_det <- function(csv, group, range_csv = NULL) {
  if (!file.exists(csv)) { message("skip ", group, " (", basename(csv), " not found)"); return(NULL) }
  d <- read_csv(csv, show_col_types = FALSE) %>%
    mutate(time = with_tz(time, TZ)) %>%
    filter(!is.na(scientific_name), !is.na(confidence))
  stopifnot("start" %in% names(d), "end" %in% names(d))
  if (!is.null(range_csv) && file.exists(range_csv)) {
    allowed <- read_csv(range_csv, show_col_types = FALSE) %>% mutate(sci = sub("_.*$", "", label))
    d <- d %>% filter(scientific_name %in% allowed$sci)
  }
  mutate(d, group = group)
}

## BirdNET v2.4 also has Orthoptera/Cicadidae classes. The species are temperate
## (N. American) so wrong at species level, but the FAMILY is plausible. We pull
## those out of the (unfiltered) bird detections and relabel to family level.
INSECT_PAT <- paste0("katydid|conehead|cricket|cicada|grasshopper|shieldback|Orthoptera|",
  "Neoconocephalus|Conocephalus|Amblycorypha|Gryllus|Tettigon|Oecanthus|Anaxipha|",
  "Allonemobius|Microcentrum|Scudderia|Pterophylla|Atlanticus|Magicicada|Neotibicen|Tibicen|Okanagana|Acheta")
insect_family <- function(sci, common) {
  g <- sub(" .*$", "", sci)
  cricket <- grepl("cricket", common, ignore.case = TRUE) |
    g %in% c("Gryllus","Acheta","Oecanthus","Anaxipha","Allonemobius","Gryllodes","Miogryllus")
  cicada  <- grepl("cicada", common, ignore.case = TRUE) |
    g %in% c("Magicicada","Neotibicen","Tibicen","Okanagana")
  ifelse(cicada, "Cicadidae", ifelse(cricket, "Gryllidae", "Tettigoniidae"))
}
load_insects <- function(csv) {
  if (!file.exists(csv)) return(NULL)
  d <- read_csv(csv, show_col_types = FALSE) %>%
    mutate(time = with_tz(time, TZ)) %>%
    filter(!is.na(scientific_name), !is.na(confidence)) %>%
    filter(grepl(INSECT_PAT, common_name, ignore.case = TRUE) |
           grepl(INSECT_PAT, scientific_name, ignore.case = TRUE))
  if (nrow(d) == 0) return(NULL)
  ## Keep GENUS as the headline (often plausible in the Neotropics), family in
  ## parens, and the matched binomial flagged approximate.
  d %>% mutate(group = "insect",
               common_name = paste0(sub(" .*$", "", scientific_name), " (",
                                     insect_family(scientific_name, common_name), ")"),
               scientific_name = paste0("≈ ", scientific_name))
}

det <- bind_rows(
  load_det(file.path(OUT, "birdnet_detections.csv"), "bird",
           file.path(OUT, "birdnet_location_species.csv")),
  load_det(file.path(OUT, "frog_detections.csv"), "frog"),  # custom model: no range filter
  load_insects(file.path(OUT, "birdnet_detections.csv"))    # BirdNET insect classes -> family
)
stopifnot(nrow(det) > 0)

det <- det %>%
  left_join(inv %>% select(folder, time, file), by = c("folder", "time")) %>%
  filter(!is.na(file)) %>%
  mutate(audio    = paste0("/", folder, "/", file),
         recorder = paste0(toupper(substr(habitat, 1, 1)), point),
         daynight = ifelse(hour(time) >= 6 & hour(time) < 18, "day", "night")) %>%
  arrange(desc(confidence)) %>%
  mutate(id = sprintf("d%05d", row_number()))

records <- det %>%
  transmute(id, audio, group, start = round(start, 2), end = round(end, 2),
            species = scientific_name, common = common_name, conf = round(confidence, 3),
            habitat, recorder, moth = moth_id,
            time = format(time, "%Y-%m-%d %H:%M"), hour = hour(time), daynight)

meta <- list(generated = format(Sys.time(), "%Y-%m-%d %H:%M"), day = DAY, n = nrow(records),
             groups = sort(unique(records$group)),
             species = sort(unique(records$common)),
             recorders = sort(unique(records$recorder)),
             habitats = sort(unique(records$habitat)))

writeLines(paste0("window.GALLERY = ",
                  toJSON(list(meta = meta, detections = records),
                         dataframe = "rows", auto_unbox = TRUE), ";"),
           file.path(site_dir, "manifest.js"))
by_grp <- paste(names(table(records$group)), table(records$group), sep = "=", collapse = ", ")
cat("Wrote", nrow(records), "detections (", by_grp, "),",
    length(meta$species), "species ->", file.path(site_dir, "manifest.js"), "\n")
