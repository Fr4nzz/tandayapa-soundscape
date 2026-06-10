#!/usr/bin/env bash
# Batch the detection pipeline for the new deployment days, then export web data.
cd "d:/Audiomoths" || exit 1
FILTER='Predicting species:|Downloading|tensorflow|WARNING|deprecated|oneDNN|built under'
for DAY in day3 day4 day5 day6; do
  echo "##### $DAY : BirdNET ($(date +%H:%M)) #####"
  TANDAYAPA_DAY=$DAY Rscript run_birdnet_day1.R 2>&1 | grep -avE "$FILTER" | grep -aE "Clips|DONE|/[0-9]+ clips|Total"
  echo "##### $DAY : location filter #####"
  TANDAYAPA_DAY=$DAY Rscript birdnet_location_filter.R 2>&1 | grep -aE "species|written"
  echo "##### $DAY : frogs #####"
  TANDAYAPA_DAY=$DAY Rscript run_frogs_day1.R 2>&1 | grep -avE "$FILTER" | grep -aE "Clips|DONE|/[0-9]+ clips|Total|Loading"
done
echo "##### export web data #####"
Rscript export_web_data.R 2>&1 | grep -avE "$FILTER" | tail -12
echo "##### ALL NEW DAYS DONE ($(date +%H:%M)) #####"
