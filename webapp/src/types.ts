export type Group = 'bird' | 'frog' | 'insect'

export interface Detection {
  id: string
  day: string          // calendar date of the detection, e.g. "2026-06-02"
  deploy?: string      // deployment block (day1..day6), tagged on load
  group: Group
  audio: string        // server-root path to the original WAV, e.g. "/F1501_A05/xxx.WAV"
  start: number        // detection start (s) within the clip
  end: number          // detection end (s)
  species: string      // scientific name
  common: string       // common name
  conf: number         // confidence 0..1
  habitat: string      // "forest" | "pasture"
  recorder: string     // "F1".."P3"
  moth: string         // AudioMoth id
  time: string         // "YYYY-MM-DD HH:MM:SS" local
  hour: number
  daynight: 'day' | 'night'
  spacing: number      // recorder spacing for the day (m)
}

export interface ReferenceCall {
  url: string          // playable audio URL (iNaturalist)
  source: string       // "iNaturalist"
  obs_url: string      // observation page
  by: string           // recordist
  place: string
  license: string
}

export interface Recording {
  deploy: string       // day1..day6
  date: string         // "YYYY-MM-DD"
  datetime: string     // "YYYY-MM-DD HH:MM:SS"
  hour: number
  daynight: 'day' | 'night'
  habitat: string
  spacing: number
  point: number
  recorder: string     // "F1".."P3"
  moth: string
  url: string          // R2 .opus URL
}

export interface DaySummary {
  day: string
  spacing: number
  window: [string, string]
  n: number
  groups: Record<string, number>
  recorders: string[]
  habitats: string[]
  species: string[]
}

export interface IndexFile {
  generated: string
  days: DaySummary[]
  groups: string[]
  recorders: string[]
  habitats: string[]
  species: string[]
}
