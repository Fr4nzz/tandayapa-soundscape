// Confidence -> colour along a warm amber → bright-moss ramp (greener = surer).
const STOPS: [number, string][] = [
  [0.25, '#8a6d3b'],
  [0.50, '#cf9a3c'],
  [0.70, '#e3c24a'],
  [0.85, '#9ccb5e'],
  [1.00, '#c6f06a'],
]

function hexToRgb(h: string) {
  const n = parseInt(h.slice(1), 16)
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255]
}
const toHex = (v: number) => Math.round(v).toString(16).padStart(2, '0')

export function confColor(c: number): string {
  const x = Math.max(STOPS[0][0], Math.min(1, c))
  for (let i = 0; i < STOPS.length - 1; i++) {
    const [a, ca] = STOPS[i], [b, cb] = STOPS[i + 1]
    if (x <= b) {
      const t = (x - a) / (b - a)
      const ra = hexToRgb(ca), rb = hexToRgb(cb)
      return `#${toHex(ra[0] + (rb[0] - ra[0]) * t)}${toHex(ra[1] + (rb[1] - ra[1]) * t)}${toHex(ra[2] + (rb[2] - ra[2]) * t)}`
    }
  }
  return STOPS[STOPS.length - 1][1]
}

// magma-ish colormap for the wavesurfer spectrogram (256 rgba rows)
export function magma(): number[][] {
  const stops: [number, number[]][] = [
    [0.0, [4, 4, 20]], [0.15, [40, 12, 70]], [0.35, [122, 28, 109]],
    [0.55, [190, 54, 90]], [0.75, [240, 110, 70]], [0.9, [251, 180, 90]], [1.0, [252, 253, 191]],
  ]
  const out: number[][] = []
  for (let i = 0; i < 256; i++) {
    const x = i / 255
    let s = 0
    while (s < stops.length - 2 && x > stops[s + 1][0]) s++
    const [a, ca] = stops[s], [b, cb] = stops[s + 1]
    const t = (x - a) / (b - a)
    out.push([
      (ca[0] + (cb[0] - ca[0]) * t) / 255,
      (ca[1] + (cb[1] - ca[1]) * t) / 255,
      (ca[2] + (cb[2] - ca[2]) * t) / 255,
      1,
    ])
  }
  return out
}

export const pad2 = (n: number) => String(n).padStart(2, '0')
export const fmtClock = (t: string) => t.slice(11, 16) // HH:MM from "YYYY-MM-DD HH:MM:SS"
export const fmtDate = (t: string) => t.slice(0, 10)
