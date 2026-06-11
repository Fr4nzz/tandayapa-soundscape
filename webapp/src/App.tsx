import { useEffect, useMemo, useState } from 'react'
import type { Detection, IndexFile, Recording, ReferenceCall } from './types'
import { Filters, DEFAULT_FILTERS, type FilterState } from './components/Filters'
import { DetectionCard } from './components/DetectionCard'
import { RecordingCard } from './components/RecordingCard'
import { SpeciesRow, type SpeciesGroup } from './components/SpeciesRow'

const DATA = `${import.meta.env.BASE_URL}data`   // detection JSON bundled with the app; audio streams from Cloudflare R2
const PAGE = 24        // detection cards per page (grid view)

export default function App() {
  const [index, setIndex] = useState<IndexFile | null>(null)
  const [dets, setDets] = useState<Detection[]>([])
  const [recs, setRecs] = useState<Recording[]>([])
  const [refMap, setRefMap] = useState<Record<string, ReferenceCall[]>>({})
  const [err, setErr] = useState<string | null>(null)
  const [f, setF] = useState<FilterState>(DEFAULT_FILTERS)
  const [page, setPage] = useState(0)

  useEffect(() => {
    const v = `?t=${Date.now()}`   // cache-bust so new days/taxa always load fresh
    fetch(`${DATA}/index.json${v}`)
      .then((r) => { if (!r.ok) throw new Error('index.json not found'); return r.json() })
      .then(async (ix: IndexFile) => {
        setIndex(ix)
        const days = await Promise.all(
          ix.days.map((d) => fetch(`${DATA}/${d.day}.json${v}`).then((r) => r.json() as Promise<Detection[]>)
            .then((arr) => arr.map((x) => ({ ...x, deploy: d.day }))))   // tag each detection with its deployment (day1..day6)
        )
        setDets(days.flat())
        fetch(`${DATA}/audio_manifest.json${v}`)
          .then((r) => (r.ok ? r.json() : []))
          .then((m: Recording[]) => setRecs(m))
          .catch(() => {})   // recordings view is optional
        fetch(`${DATA}/reference_calls.json${v}`)
          .then((r) => (r.ok ? r.json() : {}))
          .then((m: Record<string, ReferenceCall[]>) => setRefMap(m))
          .catch(() => {})   // reference calls are optional
      })
      .catch((e) => setErr(String(e.message ?? e)))
  }, [])

  const set = (p: Partial<FilterState>) => { setF((s) => ({ ...s, ...p })); setPage(0) }

  const filtered = useMemo(() => {
    const q = f.search.trim().toLowerCase()
    let out = dets.filter((d) =>
      d.conf >= f.conf &&
      (f.day === 'all' || d.deploy === f.day) &&
      (f.spacing === 'all' || String(d.spacing) === f.spacing) &&
      (f.group === 'all' || d.group === f.group) &&
      (f.habitat === 'all' || d.habitat === f.habitat) &&
      (f.recorder === 'all' || d.recorder === f.recorder) &&
      (f.daynight === 'all' || d.daynight === f.daynight) &&
      d.hour >= f.hourMin &&
      (!q || d.common.toLowerCase().includes(q) || d.species.toLowerCase().includes(q))
    )
    const s = f.sort
    out.sort((a, b) =>
      s === 'conf-asc' ? a.conf - b.conf :
      s === 'time-asc' ? a.time.localeCompare(b.time) :
      s === 'time-desc' ? b.time.localeCompare(a.time) :
      s === 'species' ? a.common.localeCompare(b.common) :
      b.conf - a.conf)
    return out
  }, [dets, f])

  // group into one row per species (top song first) for the "By species" view
  const speciesGroups = useMemo<SpeciesGroup[]>(() => {
    if (f.view !== 'species') return []
    const m = new Map<string, Detection[]>()
    for (const d of filtered) {
      const a = m.get(d.species)
      if (a) a.push(d); else m.set(d.species, [d])
    }
    const groups = [...m.values()].map((items) => ({
      species: items[0].species, common: items[0].common, group: items[0].group,
      items: items.slice().sort((a, b) => b.conf - a.conf),
    }))
    groups.sort((a, b) =>
      f.sort === 'species' ? a.common.localeCompare(b.common) : b.items[0].conf - a.items[0].conf)
    return groups
  }, [filtered, f.view, f.sort])

  // "By recording" view: browse the raw clips by site / time / habitat (audio_manifest.json)
  const filteredRecs = useMemo(() => {
    if (f.view !== 'recordings') return []
    const out = recs.filter((r) =>
      (f.day === 'all' || r.deploy === f.day) &&
      (f.spacing === 'all' || String(r.spacing) === f.spacing) &&
      (f.habitat === 'all' || r.habitat === f.habitat) &&
      (f.recorder === 'all' || r.recorder === f.recorder) &&
      (f.daynight === 'all' || r.daynight === f.daynight) &&
      r.hour >= f.hourMin
    )
    out.sort((a, b) => f.sort === 'time-desc'
      ? b.datetime.localeCompare(a.datetime) : a.datetime.localeCompare(b.datetime))
    return out
  }, [recs, f])

  const bySpecies = f.view === 'species'
  const byRecs = f.view === 'recordings'
  const unitCount = byRecs ? filteredRecs.length : bySpecies ? speciesGroups.length : filtered.length
  // species view renders all rows at once; grid + recordings views are paginated
  const pages = bySpecies ? 1 : Math.max(1, Math.ceil((byRecs ? filteredRecs.length : filtered.length) / PAGE))
  const pageItems = filtered.slice(page * PAGE, page * PAGE + PAGE)
  const pageRecs = filteredRecs.slice(page * PAGE, page * PAGE + PAGE)
  const pageGroups = speciesGroups

  return (
    <div className="relative z-10 mx-auto max-w-[1500px] px-4 pb-24 sm:px-6">
      <Header index={index} total={dets.length} />

      {err && (
        <div className="mt-8 rounded-xl border border-ember/40 bg-ember/10 p-5 font-mono text-sm text-ink">
          Couldn’t load data: {err}. Generate it with <code className="text-moss-bright">Rscript export_web_data.R</code> and serve the project root.
        </div>
      )}

      {index && (
        <div className="mt-6 grid grid-cols-1 gap-6 lg:grid-cols-[280px_1fr]">
          <Filters index={index} f={f} set={set}
            total={byRecs ? recs.length : dets.length}
            shown={byRecs ? filteredRecs.length : filtered.length} />

          <main>
            {unitCount === 0 ? (
              <div className="grid place-items-center rounded-xl border border-line bg-panel/50 py-24 font-mono text-muted">
                {byRecs ? 'No recordings match these filters.' : 'No detections match these filters.'}
              </div>
            ) : byRecs ? (
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 2xl:grid-cols-3">
                {pageRecs.map((r, i) => <RecordingCard key={r.url} rec={r} idx={i} />)}
              </div>
            ) : bySpecies ? (
              <div className="flex flex-col gap-4">
                {pageGroups.map((sp) => <SpeciesRow key={sp.species} sp={sp} />)}
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 2xl:grid-cols-3">
                {pageItems.map((d, i) => <DetectionCard key={d.id} det={d} idx={i} refs={refMap[d.species]} />)}
              </div>
            )}
            <Pager page={page} pages={pages} onPage={setPage} />
          </main>
        </div>
      )}

      {!index && !err && (
        <div className="mt-24 text-center font-mono text-muted">loading detections…</div>
      )}
    </div>
  )
}

function Header({ index, total }: { index: IndexFile | null; total: number }) {
  return (
    <header className="sticky top-0 z-20 -mx-4 mb-2 border-b border-line bg-base/80 px-4 py-4 backdrop-blur-md sm:-mx-6 sm:px-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="font-display text-[30px] font-black leading-none tracking-tight text-ink sm:text-[34px]">
            Tandayapa <span className="text-moss-bright">Soundscape</span>
          </h1>
          <p className="mt-1.5 font-mono text-[12px] text-muted">
            BirdNET birds, frogs &amp; insects · cloud-forest recorder-spacing study · verify each call by ear + spectrogram
          </p>
        </div>
        {index && (
          <div className="flex items-center gap-4 font-mono text-[12px] text-muted">
            <Stat n={total.toLocaleString()} label="detections" />
            <Stat n={String(index.days.length)} label="days" />
            <Stat n={String(index.species.length)} label="species" />
          </div>
        )}
      </div>
    </header>
  )
}

function Stat({ n, label }: { n: string; label: string }) {
  return (
    <div className="text-right">
      <div className="font-display text-[20px] font-bold text-moss-bright">{n}</div>
      <div className="text-[10px] uppercase tracking-widest text-faint">{label}</div>
    </div>
  )
}

function Pager({ page, pages, onPage }: { page: number; pages: number; onPage: (p: number) => void }) {
  if (pages <= 1) return null
  const nums: number[] = []
  for (let p = 0; p < pages; p++) if (p === 0 || p === pages - 1 || Math.abs(p - page) <= 2) nums.push(p)
  return (
    <nav className="mt-8 flex flex-wrap items-center justify-center gap-1.5 font-mono text-[13px]">
      <PBtn disabled={page === 0} onClick={() => onPage(page - 1)}>‹</PBtn>
      {nums.map((p, i) => (
        <span key={p} className="flex items-center gap-1.5">
          {i > 0 && p - nums[i - 1] > 1 && <span className="px-1 text-faint">…</span>}
          <PBtn active={p === page} onClick={() => onPage(p)}>{p + 1}</PBtn>
        </span>
      ))}
      <PBtn disabled={page === pages - 1} onClick={() => onPage(page + 1)}>›</PBtn>
    </nav>
  )
}

function PBtn({ children, active, disabled, onClick }: {
  children: React.ReactNode; active?: boolean; disabled?: boolean; onClick: () => void
}) {
  return (
    <button disabled={disabled} onClick={onClick}
      className={`min-w-[34px] rounded-md border px-2.5 py-1.5 transition ${
        active ? 'border-moss bg-moss text-base font-bold'
        : 'border-line text-muted hover:bg-panel-2 hover:text-ink disabled:opacity-30'
      }`}>
      {children}
    </button>
  )
}
