import type { IndexFile } from '../types'

export type ViewMode = 'grid' | 'species'
export interface FilterState {
  day: string; spacing: string; group: string; search: string; habitat: string
  recorder: string; daynight: string; hourMin: number; conf: number; sort: string
  view: ViewMode
}
export const DEFAULT_FILTERS: FilterState = {
  day: 'all', spacing: 'all', group: 'all', search: '', habitat: 'all',
  recorder: 'all', daynight: 'all', hourMin: 0, conf: 0.25, sort: 'conf-desc',
  view: 'grid',
}

export function Filters({
  index, f, set, total, shown,
}: {
  index: IndexFile; f: FilterState; set: (p: Partial<FilterState>) => void
  total: number; shown: number
}) {
  const dayOpts = index.days.map((d) => [d.day, `${d.window[0].slice(5, 10)} · ${d.spacing}m`] as [string, string])
  const spacings = [...new Set(index.days.map((d) => d.spacing))].sort((a, b) => a - b)
  return (
    <aside className="flex flex-col gap-5 lg:sticky lg:top-[84px] lg:h-fit">
      <div className="rounded-xl border border-line bg-panel/70 p-4 backdrop-blur-sm">
        <div className="mb-3 flex items-baseline justify-between">
          <span className="font-mono text-[11px] uppercase tracking-widest text-faint">Filter</span>
          <span className="font-mono text-[11px] text-muted">
            <span className="text-moss-bright">{shown.toLocaleString()}</span> / {total.toLocaleString()}
          </span>
        </div>

        <Field label="View">
          <Segmented value={f.view} onChange={(v) => set({ view: v as ViewMode })}
            options={[['grid', 'Grid'], ['species', 'By species ⇆']]} />
          <p className="mt-1 text-[10px] leading-tight text-faint">
            {f.view === 'species'
              ? 'one row per species · top song first · slide right for more'
              : 'every detection as its own card'}
          </p>
        </Field>

        <Field label="Taxon">
          <Segmented value={f.group} onChange={(v) => set({ group: v })}
            options={[['all', 'All'], ['bird', '🐦 Birds'], ['frog', '🐸 Frogs'], ['insect', '🦗 Insects']]} />
        </Field>

        <Field label="Day">
          <Segmented wrap value={f.day} onChange={(v) => set({ day: v })}
            options={[['all', 'All'], ...dayOpts]} />
        </Field>

        <Field label="Spacing">
          <Segmented value={f.spacing} onChange={(v) => set({ spacing: v })}
            options={[['all', 'All'], ...spacings.map((s) => [String(s), `${s} m`] as [string, string])]} />
        </Field>

        <Field label="Search species">
          <input list="species" value={f.search} onChange={(e) => set({ search: e.target.value })}
            placeholder="common or scientific…"
            className="w-full rounded-md border border-line bg-base/60 px-2.5 py-1.5 font-mono text-[13px] text-ink placeholder:text-faint focus:border-moss focus:outline-none" />
          <datalist id="species">{index.species.map((s) => <option key={s} value={s} />)}</datalist>
        </Field>

        <Field label="Habitat">
          <Segmented value={f.habitat} onChange={(v) => set({ habitat: v })}
            options={[['all', 'All'], ['forest', 'Forest'], ['pasture', 'Pasture']]} />
        </Field>

        <Field label="Recorder">
          <Segmented wrap value={f.recorder} onChange={(v) => set({ recorder: v })}
            options={[['all', 'All'], ...index.recorders.map((r) => [r, r] as [string, string])]} />
        </Field>

        <Field label="Time">
          <Segmented value={f.daynight} onChange={(v) => set({ daynight: v })}
            options={[['all', 'All'], ['day', 'Day'], ['night', 'Night']]} />
        </Field>

        <Field label={`Hour ≥ ${String(f.hourMin).padStart(2, '0')}:00`}>
          <input type="range" min={0} max={23} value={f.hourMin}
            onChange={(e) => set({ hourMin: +e.target.value })} className="w-full" />
        </Field>

        <Field label={`Min confidence · ${f.conf.toFixed(2)}`}>
          <input type="range" min={0.25} max={1} step={0.01} value={f.conf}
            onChange={(e) => set({ conf: +e.target.value })} className="w-full" />
        </Field>

        <Field label="Sort">
          <select value={f.sort} onChange={(e) => set({ sort: e.target.value })}
            className="w-full rounded-md border border-line bg-base/60 px-2.5 py-1.5 font-mono text-[13px] text-ink focus:border-moss focus:outline-none">
            <option value="conf-desc">Confidence ↓</option>
            <option value="conf-asc">Confidence ↑</option>
            <option value="time-asc">Time ↑</option>
            <option value="time-desc">Time ↓</option>
            <option value="species">Species A–Z</option>
          </select>
        </Field>

        <button onClick={() => set({ ...DEFAULT_FILTERS })}
          className="mt-1 w-full rounded-md border border-line-2 py-1.5 font-mono text-[12px] text-muted transition hover:bg-panel-2 hover:text-ink">
          Reset filters
        </button>
      </div>
    </aside>
  )
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="mb-3.5">
      <label className="mb-1.5 block font-mono text-[11px] uppercase tracking-wider text-muted">{label}</label>
      {children}
    </div>
  )
}

function Segmented({
  value, onChange, options, wrap = false,
}: {
  value: string; onChange: (v: string) => void; options: [string, string][]; wrap?: boolean
}) {
  return (
    <div className={`flex gap-1 rounded-lg border border-line bg-base/40 p-1 ${wrap ? 'flex-wrap' : ''}`}>
      {options.map(([v, label]) => (
        <button key={v} onClick={() => onChange(v)}
          className={`flex-1 rounded-md px-2 py-1 font-mono text-[12px] transition ${
            value === v ? 'bg-moss text-base font-semibold' : 'text-muted hover:text-ink'
          }`}>
          {label}
        </button>
      ))}
    </div>
  )
}
